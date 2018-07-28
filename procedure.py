from trytond.model import ModelView, ModelSQL, fields, Unique

from .galeno_mixin import CoreMixin

__all__ = ['Procedure']


class Procedure(CoreMixin, ModelSQL, ModelView):
    'Procedure'
    __name__ = 'galeno.procedure'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True, translate=True)

    @classmethod
    def __setup__(cls):
        super(Procedure, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('code_uniq', Unique(t, t.code),
             'Procedure code must be unique'),
        ]
        cls._order.insert(0, ('name', 'ASC'))

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
