from datetime import datetime

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import Eval, If, Bool
from trytond.transaction import Transaction
from trytond.pool import Pool

__all__ = ['PatientPrescription', 'PatientPrescriptionLine']


class PatientPrescription(Workflow, ModelSQL, ModelView):
    'Patient Prescription'
    __name__ = 'galeno.patient.prescription'

    professional = fields.Many2One('galeno.professional', 'Professional',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        },
        domain=[
            ('id', If(
                Bool(Eval('context', {}).get('professional', None)), '=', '!='),
                Eval('context', {}).get('professional', -1)),
        ], depends=['state'], required=True, select=True)
    code = fields.Char('Code', readonly=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ], 'State', readonly=True, required=True)
    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='RESTRICT',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], select=True)
    evaluation = fields.Many2One(
        'galeno.patient.evaluation', 'Evaluation', readonly=True)
    date = fields.DateTime('Date', required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    notes = fields.Text('Notes',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    lines = fields.One2Many('galeno.patient.prescription.line',
        'prescription', 'Prescription',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])

    @classmethod
    def __setup__(cls):
        super(PatientPrescription, cls).__setup__()
        cls._order = [
            ('date', 'DESC'),
            ]
        cls._transitions |= set((
                ('draft', 'done'),
                ('draft', 'cancel'),
                ('done', 'cancel'),
                ('cancel', 'draft'),
                ('done', 'draft'),
                ))
        cls._buttons.update({
                'cancel': {
                    'invisible': Eval('state').in_(['cancel']),
                    'depends': ['state'],
                    },
                'done': {
                    'invisible': ~Eval('state').in_(['draft']),
                    'depends': ['state'],
                    },
                'draft': {
                    'invisible': Eval('state').in_(['draft']),
                    'depends': ['state'],
                    },
                })

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_date():
        return datetime.now()

    @staticmethod
    def default_professional():
        return Transaction().context.get('professional')

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, prescriptions):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def done(cls, prescriptions):
        for prescription in prescriptions:
            prescription.date = datetime.now()
        cls.save(prescriptions)

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, prescriptions):
        pass

    def get_rec_name(self, name):
        return "%s - %s" % (self.code, self.date)

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        domain = [bool_op,
            ('code',) + tuple(clause[1:]),
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
                        config.prescription_sequence.id)
        return super(PatientPrescription, cls).create(vlist)


class PatientPrescriptionLine(ModelSQL, ModelView):
    'Patient Prescription Line'
    __name__ = 'galeno.patient.prescription.line'

    prescription = fields.Many2One('galeno.patient.prescription',
        'Prescription', required=True, readonly=True)
    prescription_state = fields.Function(
        fields.Selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ], 'Prescription State', states={'invisible': True}),
        'on_change_with_prescription_state')
    medicament = fields.Many2One('galeno.medicament', 'Medicament',
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])
    active_component = fields.Char('Active Commponent', required=True,
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])
    quantity = fields.Numeric('Quantity', digits=(16, 2),
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])
    dose = fields.Numeric('Dose', digits=(16, 2),
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])
    dose_unit = fields.Many2One(
        'galeno.medicament.dose.unit', 'Dose Unit', required=True,
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])
    frequency = fields.Many2One(
        'galeno.medicament.frequency', 'Frequency', required=True,
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])
    duration = fields.Char('Duration',
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])

    @fields.depends('medicament')
    def on_change_medicament(self):
        if self.medicament:
            self.active_component = self.medicament.composition
        else:
            self.active_component = None

    @fields.depends('prescription', '_parent_prescription.state')
    def on_change_with_prescription_state(self, name=None):
        if self.prescription:
            return self.prescription.state
        return None
