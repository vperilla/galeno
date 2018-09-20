from datetime import datetime

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import Eval, If, Bool
from trytond.transaction import Transaction
from trytond.pool import Pool

__all__ = ['PatientPrescription', 'PatientPrescriptionPharmaLine',
    'PatientPrescriptionNoPharmaLine']


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
    evaluation = fields.Many2One('galeno.patient.evaluation', 'Evaluation',
        domain=[
            If(Bool(Eval('evaluation')),
                ('patient', '=', Eval('patient')),
                ())
        ],
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['patient', 'state'])
    date = fields.DateTime('Date', required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    notes = fields.Text('Notes',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    warning = fields.Text('Warning',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    pharma_lines = fields.One2Many('galeno.patient.prescription.pharma.line',
        'prescription', 'Prescription',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    no_pharma_lines = fields.One2Many(
        'galeno.patient.prescription.no.pharma.line',
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
                ('cancel', 'draft'),
                ('done', 'draft'),
                ))
        cls._buttons.update({
                'cancel': {
                    'invisible': ~Eval('state').in_(['draft']),
                    'icon': 'tryton-cancel',
                    'depends': ['state'],
                    },
                'done': {
                    'invisible': ~Eval('state').in_(['draft']),
                    'icon': 'tryton-ok',
                    'depends': ['state'],
                    },
                'draft': {
                    'invisible': Eval('state').in_(['draft']),
                    'icon': 'tryton-undo',
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

    @fields.depends('evaluation', 'patient')
    def on_change_evaluation(self):
        if self.evaluation and not self.patient:
            self.patient = self.evaluation.patient

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
                        config.get_multivalue('prescription_sequence').id)
        return super(PatientPrescription, cls).create(vlist)


class PatientPrescriptionPharmaLine(ModelSQL, ModelView):
    'Patient Prescription Pharma Line'
    __name__ = 'galeno.patient.prescription.pharma.line'

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
        }, depends=['prescription_state'], required=True)
    active_component = fields.Function(
        fields.Text('Active Commponent'), 'on_change_with_active_component')
    quantity = fields.Char('Prescription Quantity',
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'], required=True)
    dose = fields.Char('Dose',
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'], required=True)
    frequency = fields.Many2One(
        'galeno.medicament.frequency', 'Frequency', required=True,
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])
    duration = fields.Char('Duration',
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])
    administration_route = fields.Function(fields.Char('Administration Route'),
        'on_change_with_administration_route')

    @fields.depends('prescription', '_parent_prescription.state')
    def on_change_with_prescription_state(self, name=None):
        if self.prescription:
            return self.prescription.state
        return None

    @fields.depends('medicament')
    def on_change_with_administration_route(self, name=None):
        if self.medicament and self.medicament.administration_route:
            return self.medicament.administration_route
        return None

    @fields.depends('medicament')
    def on_change_with_active_component(self, name=None):
        if self.medicament:
            return self.medicament.composition
        return None


class PatientPrescriptionNoPharmaLine(ModelSQL, ModelView):
    'Patient Prescription No Pharma Line'
    __name__ = 'galeno.patient.prescription.no.pharma.line'

    prescription = fields.Many2One('galeno.patient.prescription',
        'Prescription', required=True, readonly=True)
    prescription_state = fields.Function(
        fields.Selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ], 'Prescription State', states={'invisible': True}),
        'on_change_with_prescription_state')
    notes = fields.Text('Notes',
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])
    dose = fields.Char('Dose',
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'], required=True)
    frequency = fields.Many2One(
        'galeno.medicament.frequency', 'Frequency', required=True,
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])
    duration = fields.Char('Duration',
        states={
            'readonly': ~Eval('prescription_state').in_(['draft']),
        }, depends=['prescription_state'])

    @fields.depends('prescription', '_parent_prescription.state')
    def on_change_with_prescription_state(self, name=None):
        if self.prescription:
            return self.prescription.state
        return None
