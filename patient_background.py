from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pyson import Eval


__all__ = ['Medicament', 'Disease', 'Family', 'Surgery', 'Test']


class Medicament(ModelSQL, ModelView):
    'Galeno Medicament Background'
    __name__ = 'galeno.patient.background.medicament'

    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='RESTRICT')
    medicament = fields.Many2One(
        'galeno.medicament', 'Medicament', required=True, ondelete='RESTRICT')
    quantity = fields.Char('Amount', required=True,
        help="Ex. 8 pills per day")
    notes = fields.Text('Notes')

    @classmethod
    def __setup__(cls):
        super(Medicament, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('medicament_uniq', Unique(t, t.patient, t.medicament),
             'Medicament must be unique'),
        ]


class Disease(ModelSQL, ModelView):
    "Galeno Disease Background"
    __name__ = 'galeno.patient.background.disease'

    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='RESTRICT')
    disease = fields.Many2One('galeno.disease', 'Disease', required=True)
    notes = fields.Text('Notes')

    @classmethod
    def __setup__(cls):
        super(Disease, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('disease_uniq', Unique(t, t.patient, t.disease),
             'Disease must be unique'),
        ]


class Family(ModelSQL, ModelView):
    "Galeno Family Background"
    __name__ = "galeno.patient.background.family"

    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='RESTRICT')
    relationship = fields.Char('Relationship', required=True,
        help="Mother, Father, Uncle, etc.")
    disease = fields.Many2One('galeno.disease', 'Disease', required=True)
    notes = fields.Text('Notes')

    @classmethod
    def __setup__(cls):
        super(Family, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('disease_uniq', Unique(t, t.patient, t.relationship, t.disease),
             'Disease per relation must be unique'),
        ]


class Surgery(ModelSQL, ModelView):
    "Galeno Surgery Background"
    __name__ = "galeno.patient.background.surgery"

    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='RESTRICT')
    # TODO: add procedures
    notes = fields.Text('Notes')


class Test(ModelSQL, ModelView):
    "Galeno Test Background"
    __name__ = 'galeno.patient.background.test'

    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='RESTRICT')
    patient_gender = fields.Function(fields.Char('Patient gender',
        states={
            'invisible': True,
        }), 'on_change_with_patient_gender')
    test = fields.Many2One('galeno.test', 'Test', required=True,
        domain=[['OR',
            ('gender', '=', Eval('patient_gender')),
            ('gender', '=', 'unisex')]
        ], depends=['patient_gender'])
    notes = fields.Text('Notes')

    @fields.depends('patient')
    def on_change_with_patient_gender(self, name=None):
        if self.patient:
            return self.patient.gender
        return None
