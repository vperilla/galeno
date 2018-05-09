from sql.conditionals import Coalesce
from sql.operators import Equal
from trytond.model import ModelView, ModelSQL, fields, Unique, Exclude

__all__ = ['TestCategory', 'Test']


class TestCategory(ModelSQL, ModelView):
    "Test Category"
    __name__ = "galeno.test.category"
    name = fields.Char('Name', required=True, translate=True)
    parent = fields.Many2One('galeno.test.category', 'Parent', select=True)
    childs = fields.One2Many('galeno.test.category', 'parent',
            string='Children')

    @classmethod
    def __setup__(cls):
        super(TestCategory, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_parent_exclude',
                Exclude(t, (t.name, Equal), (Coalesce(t.parent, -1), Equal)),
                'The name of a test category must be unique by parent.'),
            ('name_uniq', Unique(t, t.name), 'Category name must be unique'),
            ]
        cls._order.insert(0, ('name', 'ASC'))

    @classmethod
    def validate(cls, categories):
        super(TestCategory, cls).validate(categories)
        cls.check_recursion(categories, rec_name='name')

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + ' / ' + self.name
        else:
            return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if isinstance(clause[2], basestring):
            values = clause[2].split('/')
            values.reverse()
            domain = []
            field = 'name'
            for name in values:
                domain.append((field, clause[1], name.strip()))
                field = 'parent.' + field
        else:
            domain = [('name',) + tuple(clause[1:])]
        ids = [w.id for w in cls.search(domain, order=[])]
        return [('parent', 'child_of', ids)]


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
