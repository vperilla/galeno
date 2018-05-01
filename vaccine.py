from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.transaction import Transaction

__all__ = ['Vaccine']


class Vaccine(ModelSQL, ModelView):
    'Vaccine'
    __name__ = 'galeno.vaccine'

    company = fields.Many2One('company.company', 'Company', required=True)
    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    description = fields.Text('Description')

    @classmethod
    def __setup__(cls):
        super(Vaccine, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('code_uniq', Unique(t, t.company, t.code), 'Code must be unique'),
        ]

    @staticmethod
    def default_company():
        return Transaction().context.get('company')
