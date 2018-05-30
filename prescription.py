from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import Eval, If
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = ['PatientPrescription', 'PatientPrescriptionLine']


class PatientPrescription(Workflow, ModelSQL, ModelView):
    'Patient Prescription'
    __name__ = 'galeno.patient.prescription'
    _history = True

    professional = fields.Many2One('galeno.professional', 'Professional',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        },
        domain=[
            ('id', If(Eval('context', {}).contains('professional'), '=', '!='),
                Eval('context', {}).get('professional', -1)),
        ], depends=['state'], required=True, select=True)
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
    date = fields.Date('Date', required=True,
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
                })

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_professional():
        return Transaction().context.get('professional')

    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def done(cls, prescriptions):
        pool = Pool()
        Date = pool.get('ir.date')
        for prescription in prescriptions:
            prescription.date = Date.today()
        cls.save(prescriptions)

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, prescriptions):
        pass


class PatientPrescriptionLine(ModelSQL, ModelView):
    'Patient Prescription Line'
    __name__ = 'galeno.patient.prescription.line'

    prescription = fields.Many2One(
        'galeno.patient.prescription', 'Prescription', required=True)
    medicament = fields.Many2One('galeno.medicament', 'Medicament')
    description = fields.Char('Description', required=True)
    active_component = fields.Char('Active Commponent', required=True)
    quantity = fields.Numeric('Quantity', digits=(16, 2))
    dose = fields.Numeric('Dose', digits=(16, 2))
    dose_unit = fields.Many2One(
        'galeno.medicament.dose.unit', 'Dose Unit', required=True)
    frequency = fields.Many2One(
        'galeno.medicament.frequency', 'Frequency', required=True)

    @fields.depends('medicament')
    def on_change_medicament(self):
        if self.medicament:
            self.description = self.medicament.name
            self.active_component = self.medicament.composition
        else:
            self.description = None
            self.active_component = None
