from datetime import datetime

from sql.conditionals import Case

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import Eval, If
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.tools import reduce_ids, grouped_slice

__all__ = ['PatientAppointment']


class PatientAppointment(Workflow, ModelSQL, ModelView):
    'Patient Appointment'
    __name__ = 'galeno.patient.appointment'

    code = fields.Char('Code', readonly=True)
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
        cls._transitions |= set((
                ('scheduled', 'accomplished'),
                ('scheduled', 'patient_cancel'),
                ('scheduled', 'professional_cancel'),
                ))
        cls._buttons.update({
                'patient_cancel': {
                    'invisible': ~Eval('state').in_(['scheduled']),
                    'depends': ['state'],
                    },
                'professional_cancel': {
                    'invisible': ~Eval('state').in_(['scheduled']),
                    'depends': ['state'],
                    },
                'accomplished': {
                    'invisible': ~Eval('state').in_(['scheduled']),
                    'depends': ['state'],
                    },
                })

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

    @fields.depends('start_date', 'end_date')
    def on_change_start_date(self):
        pool = Pool()
        Configuration = pool.get('galeno.configuration')
        config = Configuration(1)
        if self.start_date:
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
        return "%s - %s" % (self.code, self.patient.rec_name)

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        domain = [bool_op,
            ('code',) + tuple(clause[1:]),
            ('patient',) + tuple(clause[1:]),
            ]
        return domain

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Config = pool.get('galeno.configuration')

        vlist = [x.copy() for x in vlist]
        config = Config(1)
        for values in vlist:
            if values.get('code') is None:
                values['code'] = Sequence.get_id(
                        config.appointment_sequence.id)
        return super(PatientAppointment, cls).create(vlist)