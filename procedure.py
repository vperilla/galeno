from trytond.model import ModelView, ModelSQL, fields, Unique

__all__ = ['Procedure']


class Procedure(ModelSQL, ModelView):
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
