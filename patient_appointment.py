from pytz import timezone, utc
from datetime import datetime, timedelta

from sql.conditionals import Case

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import Eval, If
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.tools import reduce_ids, grouped_slice

import galeno_tools

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
            'readonly': ~Eval('state').in_(['scheduled']),
        },
        domain=[
            ('id', If(Eval('context', {}).contains('professional'), '=', '!='),
                Eval('context', {}).get('professional', -1)),
        ], depends=['state'], required=True, select=True)
    start_date = fields.DateTime('Start Date', required=True,
        states={
            'readonly': ~Eval('state').in_(['scheduled']),
        }, depends=['state'])
    end_date = fields.DateTime('End Date', required=True,
        states={
            'readonly': ~Eval('state').in_(['scheduled']),
        }, depends=['state'])
    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='RESTRICT',
        states={
            'readonly': ~Eval('state').in_(['scheduled']),
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
            'readonly': ~Eval('state').in_(['scheduled']),
        }, depends=['state'])

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
                })
        cls._transitions |= set((
                ('scheduled', 'accomplished'),
                ('scheduled', 'patient_cancel'),
                ('scheduled', 'professional_cancel'),
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
                })

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_state():
        return 'scheduled'

    @staticmethod
    def default_start_date():
        return datetime.now()

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
            tz = timezone(self.company.timezone)
            local_dt = utc.localize(
                self.start_date, is_dst=None).astimezone(tz)
            if not local_dt.hour:
                start_date = datetime(*(self.start_date.date().timetuple()[:6]))
                next_date = start_date + timedelta(days=1)
                appointments_of_day = self.__class__.search([
                    ('start_date', '>=', start_date),
                    ('end_date', '<=', next_date),
                    ('professional', '=', self.professional)
                ], order=[('start_date', 'DESC')], limit=1)
                if appointments_of_day:
                    self.start_date = appointments_of_day[0].end_date
                else:
                    initial_time = config.attention_start
                    self.start_date = self.start_date + timedelta(
                        hours=initial_time.hour, minutes=initial_time.minute)
            self.end_date = self.start_date + config.appointment_duration

    @classmethod
    @ModelView.button
    @Workflow.transition('accomplished')
    def accomplished(cls, appointments):
        pass

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
        local_date = galeno_tools.format_datetime(
            self.start_date, self.company.timezone)
        return "%s - %s" % (self.patient.rec_name, local_date)

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
