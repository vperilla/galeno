from trytond.model import ModelView, ModelSQL, fields, Unique

__all__ = ['TestCategory', 'Test']


class TestCategory(ModelSQL, ModelView):
    "Test Category"
    __name__ = "galeno.test.category"
    name = fields.Char('Name', required=True, translate=True)

    @classmethod
    def __setup__(cls):
        super(TestCategory, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_uniq', Unique(t, t.name), 'Category name must be unique'),
            ]
        cls._order.insert(0, ('name', 'ASC'))


class Test(ModelSQL, ModelView):
    'Galeno Test'
    __name__ = 'galeno.test'

    category = fields.Many2One(
        'galeno.test.category', 'Category', required=True)
    name = fields.Char('Name', translate=True, required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    ], 'Gender', required=True, sort=False)

    @classmethod
    def __setup__(cls):
        super(Test, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_uniq', Unique(t, t.name), 'Test name must be unique'),
            ]
        cls._order.insert(0, ('name', 'ASC'))

    def get_rec_name(self, name):
        return '%s / %s' % (self.category.rec_name, self.name)
