from pendulum import instance, from_timestamp
from datetime import datetime, timedelta

from sql.conditionals import Case

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import Eval, If, Bool
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.tools import reduce_ids, grouped_slice

from . import galeno_tools

__all__ = ['PatientAppointment']


class PatientAppointment(Workflow, ModelSQL, ModelView):
    'Patient Appointment'
    __name__ = 'galeno.patient.appointment'

    company = fields.Many2One('company.company', 'Company', required=True,
        states={
            'invisible': True,
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
                    'icon': 'tryton-go-previous',
                    'depends': ['state'],
                    },
                })

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

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
                    (table.state == 'scheduled', 'khaki'),
                    (table.state == 'accomplished', 'lightgreen'),
                    else_='lightcoral'),
                where=red_sql,
            )
            cursor.execute(*query)
            result.update(dict(cursor.fetchall()))
        return result

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
                    if config.attention_start:
                        initial_time = config.attention_start
                        self.start_date = (self.start_date +
                            timedelta(hours=initial_time.hour,
                            minutes=initial_time.minute))
                    else:
                        self.raise_user_error('without_start')
            self.end_date = self.start_date + config.appointment_duration
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
