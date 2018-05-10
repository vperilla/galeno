from trytond.model import ModelView, ModelSQL, fields, Unique

__all__ = ['ContraceptiveMethod']


class ContraceptiveMethod(ModelSQL, ModelView):
    'Occupation'
    __name__ = 'galeno.contraceptive.method'

    name = fields.Char('Name', required=True, translate=True)
    gender = fields.Selection([
            ('male', 'Male'),
            ('female', 'Female'),
            ('unisex', 'Unisex'),
    ], 'Gender', required=True)
    description = fields.Text('Description')

    @classmethod
    def __setup__(cls):
        super(ContraceptiveMethod, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_gender_uniq', Unique(t, t.name, t.gender),
             'Name must be unique per gender!'),
        ]
