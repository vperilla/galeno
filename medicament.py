from trytond.model import (ModelView, ModelSQL, fields, DeactivableMixin,
    Unique)
from trytond.transaction import Transaction

from .galeno_mixin import BasicMixin

__all__ = ['Medicament', 'MedicamentDoseUnit', 'MedicamentFrequency']


class Medicament(DeactivableMixin, ModelSQL, ModelView):
    'Medicament'
    __name__ = 'galeno.medicament'

    company = fields.Many2One('company.company', 'Company', required=True)
    code = fields.Char(
        'Code - Registration number', help='Sanitary registration number')
    name = fields.Char('Name', required=True)
    laboratory = fields.Char('Laboratory name')
    presentation = fields.Char('Presentation')
    type_ = fields.Char('Type', help="Generic or Brand")
    sale_kind = fields.Char(
        'Sale kind', help="Free or under prescription")
    administration_route = fields.Char('Administration route')
    composition = fields.Text('Composition', required=True,
        help="Active principle")
    notes = fields.Text('Notes')

    # TODO: check unique constraint

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @classmethod
    def search_rec_name(cls, name, clause):
        _, operator, value = clause
        if operator.startswith('!') or operator.startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        domain = [bool_op,
            ('name', operator, value),
            ('composition', operator, value),
            ]
        return domain


class MedicamentDoseUnit(ModelSQL, ModelView):
    'Dose Unit'
    __name__ = 'galeno.medicament.dose.unit'

    name = fields.Char('Unit', required=True, select=True, translate=True)
    description = fields.Char('Description', translate=True)

    @classmethod
    def __setup__(cls):
        super(MedicamentDoseUnit, cls).__setup__()
        t = cls.__table__()

        cls._sql_constraints = [
            ('name_uniq', Unique(t, t.name), 'Name must be unique !'),
        ]


class MedicamentFrequency(ModelSQL, ModelView):
    'Medicament Frequency'
    __name__ = 'galeno.medicament.frequency'

    name = fields.Char('Frequency', required=True, select=True, translate=True,
        help='Common frequency name')

    @classmethod
    def __setup__(cls):
        super(MedicamentFrequency, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_uniq', Unique(t, t.name), 'Name must be unique !'),
        ]
