from trytond.model import ModelView, ModelSQL, fields, Unique

__all__ = ['Vaccine']


class Vaccine(ModelSQL, ModelView):
    'Vaccine'
    __name__ = 'galeno.vaccine'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)

    @classmethod
    def __setup__(cls):
        super(Vaccine, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('code_uniq', Unique(t, t.code), 'Code must be unique'),
        ]

    def get_rec_name(self, name):
        return "%s: %s" % (self.code, self.name)

    @classmethod
    def search_rec_name(cls, name, clause):
        _, operator, value = clause
        if operator.startswith('!') or operator.startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        domain = [bool_op,
            ('code', operator, value),
            ('name', operator, value),
            ]
        return domain
