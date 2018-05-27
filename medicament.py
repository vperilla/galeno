from trytond.model import ModelView, ModelSQL, fields, DeactivableMixin
from trytond.transaction import Transaction

__all__ = ['Medicament']


class Medicament(DeactivableMixin, ModelSQL, ModelView):
    'Medicament'
    __name__ = 'galeno.medicament'

    company = fields.Many2One('company.company', 'Company', required=True)
    code = fields.Char(
        'Code - Registration number', help='Sanitary registration number')
    name = fields.Char('Name', required=True)
    release_date = fields.DateTime('Release date')
    expiration_date = fields.DateTime('Expiration date')
    laboratory = fields.Char('Laboratory name')
    presentation = fields.Char('Presentation')
    type_ = fields.Char('Type', help="Generic or Brand")
    sale_kind = fields.Char(
        'Sale kind', required=True, help="Free or under prescription")
    administration_route = fields.Char('Administration route')
    composition = fields.Text('Composition', required=True,
        help="Active principle")
    notes = fields.Text('Notes')

    # TODO: check unique constraint

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_type_():
        return 'generic'

    @staticmethod
    def default_sale_kind():
        return 'free'

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
