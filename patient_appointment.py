from pendulum import instance, from_timestamp
from datetime import datetime, timedelta
from email.header import Header
from email.utils import formataddr, getaddresses

from sql.conditionals import Case

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import Eval, If, Bool
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.tools import reduce_ids, grouped_slice
from trytond.report import get_email
from trytond.config import config
from trytond.sendmail import sendmail_transactional, SMTPDataManager

from . import galeno_tools

__all__ = ['PatientAppointment', 'PatientAppointmentEmailLog']


class PatientAppointment(Workflow, ModelSQL, ModelView):
    'Patient Appointment'
    __name__ = 'galeno.patient.appointment'

    company = fields.Many2One('company.company', 'Company', required=True,
        states={
            'invisible': True,
        })
    type_ = fields.Selection(
        [
            ('appointment', 'Appointment'),
            ('procedure', 'Procedure'),
        ], 'Type', required=True, sort=False)
    procedure = fields.Many2One('galeno.procedure', 'Procedure',
        states={
            'invisible': (Eval('type_') != 'procedure'),
        })
    professional = fields.Many2One('galeno.professional', 'Professional',
        states={
            'readonly': ~Eval('state').in_(['scheduled']) | (
                Eval('context', {}).get('readonly')),
        },
        domain=[
            ('id', If(Bool(
                Eval('context', {}).get('professional', None)), '=', '!='),
                Eval('context', {}).get('professional', -1)),
        ], depends=['state'], required=True, select=True)
    start_date = fields.DateTime('Start Date', required=True,
        states={
            'readonly': ~Eval('state').in_(['scheduled']) | (
                Eval('context', {}).get('readonly')),
        }, depends=['state'])
    end_date = fields.DateTime('End Date', required=True,
        states={
            'readonly': ~Eval('state').in_(['scheduled']) | (
                Eval('context', {}).get('readonly')),
        }, depends=['state'])
    patient = fields.Many2One(
        'galeno.patient', 'Patient', ondelete='RESTRICT',
        states={
            'readonly': ~Eval('state').in_(['scheduled']) | (
                Eval('context', {}).get('readonly')),
        }, depends=['state'], select=True)
    state = fields.Selection(
        [
            ('scheduled', 'Scheduled'),
            ('accomplished', 'Accomplished'),
            ('patient_cancel', 'Canceled by patient'),
            ('professional_cancel', 'Canceled by Doctor'),
        ], 'State', readonly=True, required=True)
    color = fields.Function(fields.Char('color'), 'get_color')
    notes = fields.Text('Notes',
        states={
            'readonly': ~Eval('state').in_(['scheduled']) | (
                Eval('context', {}).get('readonly')),
        }, depends=['state'])
    appointments_of_day = fields.Function(
        fields.Many2Many('galeno.patient.appointment', None, None,
            'Appointments of day',
            context={
                'readonly': True
            }), 'on_change_with_appointments_of_day')

    @classmethod
    def __setup__(cls):
        super(PatientAppointment, cls).__setup__()
        cls._order = [
            ('start_date', 'DESC'),
            ('id', 'DESC'),
            ]
        cls._error_messages.update({
                'appointments_overlap': ('"%(first)s" and "%(second)s" '
                    'appointments overlap.'),
                'accomplished_future_error': ('A future appointment can\'t be '
                    'accomplished.'),
                'scheduled_past_error': ('You can\'t scheduled on a past '
                    'date.'),
                'modify_date_appointment': ('You can modify dates only on'
                    'scheduled appointments. Error: "%(appointment)s"'),
                'without_start': 'There is no start time configuration',
                })
        cls._transitions |= set((
                ('scheduled', 'accomplished'),
                ('scheduled', 'patient_cancel'),
                ('scheduled', 'professional_cancel'),
                ('patient_cancel', 'scheduled'),
                ('professional_cancel', 'scheduled'),
                ('accomplished', 'scheduled'),
                ))
        cls._buttons.update({
                'patient_cancel': {
                    'invisible': ~Eval('state').in_(['scheduled']),
                    'icon': 'tryton-cancel',
                    'depends': ['state'],
                    },
                'professional_cancel': {
                    'invisible': ~Eval('state').in_(['scheduled']),
                    'icon': 'tryton-cancel',
                    'depends': ['state'],
                    },
                'accomplished': {
                    'invisible': ~Eval('state').in_(['scheduled']),
                    'icon': 'tryton-ok',
                    'depends': ['state'],
                    },
                'scheduled': {
                    'invisible': Eval('state').in_(['scheduled']),
                    'icon': 'tryton-undo',
                    'depends': ['state'],
                    },
                })

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_type_():
        return 'appointment'

    @staticmethod
    def default_state():
        return 'scheduled'

    @staticmethod
    def default_professional():
        return Transaction().context.get('professional')

    @classmethod
    def get_color(cls, appointments, name):
        cursor = Transaction().connection.cursor()
        table = cls.__table__()
        result = {}

        ids = [a.id for a in appointments]
        for sub_ids in grouped_slice(ids):
            red_sql = reduce_ids(table.id, sub_ids)
            query = table.select(
                table.id,
                Case(
                    ((table.state == 'scheduled') &
                     (table.type_ == 'appointment'), 'khaki'),
                    ((table.state == 'scheduled') &
                     (table.type_ == 'procedure'), 'skyblue'),
                    (table.state == 'accomplished', 'lightgreen'),
                    else_='lightcoral'),
                where=red_sql,
            )
            cursor.execute(*query)
            result.update(dict(cursor.fetchall()))
        return result

    @fields.depends('type_', 'procedure')
    def on_change_type_(self):
        if self.type_ == 'appointment':
            self.procedure = None

    @fields.depends('company', 'start_date', 'end_date', 'professional')
    def on_change_start_date(self):
        pool = Pool()
        Configuration = pool.get('galeno.configuration')
        config = Configuration(1)
        if self.start_date and self.professional:
            utc_dt = instance(self.start_date, tz='UTC')
            local_dt = utc_dt.in_timezone(self.company.timezone)
            if local_dt.hour == 0 and local_dt.minute == 0:
                app_of_day = self.on_change_with_appointments_of_day()
                if app_of_day:
                    self.start_date = self.__class__(app_of_day.pop()).end_date
                else:
                    if config.get_multivalue('attention_start'):
                        initial_time = config.get_multivalue('attention_start')
                        self.start_date = (self.start_date +
                            timedelta(hours=initial_time.hour,
                            minutes=initial_time.minute))
                    else:
                        self.raise_user_error('without_start')
            self.end_date = self.start_date + config.get_multivalue(
                'appointment_duration')
        else:
            self.end_date = None

    @fields.depends('company', 'start_date', 'professional')
    def on_change_with_appointments_of_day(self, name=None):
        if self.start_date and self.company:
            diff = abs(from_timestamp(0, self.company.timezone).offset_hours)
            utc_dt = instance(self.start_date, tz='UTC')
            local_dt = utc_dt.in_timezone(self.company.timezone)
            start_of = local_dt.start_of('day') + timedelta(hours=diff)
            start_date = datetime.combine(start_of.date(), start_of.time())
            next_date = start_date + timedelta(days=1)
            appointments_of_day = self.__class__.search([
                ('start_date', '>=', start_date),
                ('end_date', '<=', next_date),
                ('professional', '=', self.professional)
            ], order=[('start_date', 'ASC')])
            if appointments_of_day:
                return [app.id for app in appointments_of_day]
        return []

    @classmethod
    @ModelView.button
    @Workflow.transition('scheduled')
    def scheduled(cls, appointments):
        for appointment in appointments:
            now = datetime.now()
            if appointment.start_date < now:
                cls.raise_user_error('scheduled_past_error', {
                    'appointment': appointment.rec_name,
                })

    @classmethod
    @ModelView.button
    @Workflow.transition('accomplished')
    def accomplished(cls, appointments):
        for appointment in appointments:
            if appointment.start_date > datetime.now():
                cls.raise_user_error('accomplished_future_error')

    @classmethod
    @ModelView.button
    @Workflow.transition('patient_cancel')
    def patient_cancel(cls, appointments):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('professional_cancel')
    def professional_cancel(cls, appointments):
        pass

    def get_rec_name(self, name):
        if self.patient:
            local_date = galeno_tools.format_datetime(
                self.start_date, self.company.timezone)
            return "%s - %s" % (local_date, self.patient.rec_name)
        else:
            return self.notes

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        domain = [bool_op,
            ('patient',) + tuple(clause[1:]),
            ]
        return domain

    @classmethod
    def validate(cls, appointments):
        super(PatientAppointment, cls).validate(appointments)
        for appointment in appointments:
            appointment.check_dates()

    def check_dates(self):
        cursor = Transaction().connection.cursor()
        table = self.__table__()
        cursor.execute(*table.select(table.id,
                where=(((table.start_date < self.start_date)
                        & (table.end_date > self.start_date))
                    | ((table.start_date < self.end_date)
                        & (table.end_date > self.end_date))
                    | ((table.start_date > self.start_date)
                        & (table.end_date < self.end_date))
                    | ((table.start_date == self.start_date)
                       & (table.end_date == self.end_date)))
                & (table.professional == self.professional.id)
                & (table.company == self.company.id)
                & (table.state == 'scheduled')
                & (table.id != self.id)))
        appointment_id = cursor.fetchone()
        if appointment_id:
            overlapping_appointment = self.__class__(appointment_id[0])
            self.raise_user_error('appointments_overlap', {
                    'first': self.rec_name,
                    'second': overlapping_appointment.rec_name,
                    })

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        for appointments, values in zip(actions, actions):
            if 'start_date' in values or 'end_date' in values:
                for appointment in appointments:
                    if appointment.state != 'scheduled':
                        cls.raise_user_error('modify_date_appointment', {
                            'appointment': appointment.rec_name,
                        })
        super(PatientAppointment, cls).write(*args)

    @classmethod
    def send_reminder_emails(cls):
        """Cron method send reminder emails.
        """
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        after_tomorrow = tomorrow + timedelta(days=1)
        appointments = cls.search([
            ('start_date', '>', tomorrow),
            ('start_date', '<', after_tomorrow),
            ('state', '=', 'scheduled'),
        ])
        for appointment in appointments:
            appointment.send_email()

    def send_email(self):
        pool = Pool()
        datamanager = SMTPDataManager()
        Configuration = pool.get('ir.configuration')
        Lang = pool.get('ir.lang')
        Template = pool.get('ir.action.report')
        Log = pool.get('galeno.patient.appointment.email.log')

        from_ = config.get('email', 'from')
        to = []
        name = str(Header(self.patient.rec_name))
        to.append(formataddr((name, self.patient.email)))
        cc = []
        bcc = []
        languages = set()
        lang, = Lang.search([
                ('code', '=', Configuration.get_language()),
                ], limit=1)
        languages.add(lang)

        Data = pool.get('ir.model.data')
        template_id = Data.get_id('galeno', 'appointment_email')
        template = Template(template_id)

        msg = self._email(from_, to, cc, bcc, languages, template)
        to_addrs = [e for _, e in getaddresses(to + cc + bcc)]
        if to_addrs:
            if not pool.test:
                sendmail_transactional(
                    from_, to_addrs, msg, datamanager=datamanager)
            Log.create([self._email_log(msg)])

    def _email(self, from_, to, cc, bcc, languages, template):
        # TODO order languages to get default as last one for title
        msg, title = get_email(template, self, languages)
        msg['From'] = from_
        msg['To'] = ', '.join(to)
        msg['Cc'] = ', '.join(cc)
        msg['Bcc'] = ', '.join(bcc)
        msg['Subject'] = Header(title, 'utf-8')
        msg['Auto-Submitted'] = 'auto-generated'
        return msg

    def _email_log(self, msg):
        return {
            'recipients': msg['To'],
            'recipients_secondary': msg['Cc'],
            'recipients_hidden': msg['Bcc'],
            'appointment': self.id,
            }


class PatientAppointmentEmailLog(ModelSQL, ModelView):
    "Appointment Email Log"
    __name__ = 'galeno.patient.appointment.email.log'
    date = fields.Function(fields.DateTime("Date"), 'get_date')
    recipients = fields.Char("Recipients")
    recipients_secondary = fields.Char("Secondary Recipients")
    recipients_hidden = fields.Char("Hidden Recipients")
    appointment = fields.Many2One(
        'galeno.patient.appointment', 'Appointment', required=True)

    def get_date(self, name):
        return self.create_date.replace(microsecond=0)

    @classmethod
    def search_date(cls, name, clause):
        return [('create_date',) + tuple(clause[1:])]

    @staticmethod
    def order_date(tables):
        table, _ = tables[None]
        return [table.create_date]
