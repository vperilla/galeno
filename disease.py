from sql.conditionals import Coalesce
from sql.operators import Equal

from trytond.model import ModelView, ModelSQL, fields, Unique, Exclude

__all__ = ['DiseaseCategory', 'DiseaseGroup', 'Disease', 'DiseaseMembers']

SEPARATOR = ' / '


class DiseaseCategory(ModelSQL, ModelView):
    'Disease Categories'
    __name__ = 'galeno.disease.category'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True, translate=True)
    parent = fields.Many2One(
        'galeno.disease.category', 'Parent')
    childs = fields.One2Many(
        'galeno.disease.category', 'parent', 'Children')

    @classmethod
    def __setup__(cls):
        super(DiseaseCategory, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_parent_exclude',
                Exclude(t, (t.name, Equal), (Coalesce(t.parent, -1), Equal)),
                'The name of a party category must be unique by parent.'),
            ('name_uniq', Unique(t, t.name), 'Category name must be unique'),
            ]
        cls._error_messages.update({
            'wrong_name': ('Invalid category name "%%s": You can not use '
                '"%s" in name field.' % SEPARATOR),
            })
        cls._order.insert(0, ('name', 'ASC'))

    @classmethod
    def validate(cls, categories):
        super(DiseaseCategory, cls).validate(categories)
        cls.check_recursion(categories, rec_name='name')
        for category in categories:
            category.check_name()

    def check_name(self):
        if SEPARATOR in self.name:
            self.raise_user_error('wrong_name', (self.name,))

    def get_rec_name(self, name):
        if self.parent:
            return self.parent.get_rec_name(name) + SEPARATOR + self.name
        return self.name


class DiseaseGroup(ModelSQL, ModelView):
    'Disease Group'
    __name__ = 'galeno.disease.group'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True, translate=True)
    description = fields.Char('Short description', required=True)
    information = fields.Text('Detailed information')
    diseases = fields.Many2Many('galeno.disease.group.member',
        'group', 'disease', 'Diseases', readonly=True)

    @classmethod
    def __setup__(cls):
        super(DiseaseGroup, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('code_uniq', Unique(t, t.code),
             'Disease Group code must be unique'),
        ]


class Disease(ModelSQL, ModelView):
    'Disease ICD10'
    __name__ = 'galeno.disease'

    code = fields.Char('Code', required=True, help='Disease code (eg, ICD-10)')
    name = fields.Char('Name', required=True, translate=True)
    category = fields.Many2One(
        'galeno.disease.category', 'Main Category',
        help='Select the main category for this disease This is usually'
        ' associated to the standard. For instance, the chapter on the ICD-10'
        ' will be the main category for de disease')

    groups = fields.Many2Many(
        'galeno.disease.group.member', 'disease', 'group',
        'Groups', help='Specify the groups this pathology belongs. Some'
        ' automated processes act upon the code of the group')

    chromosome = fields.Char('Affected Chromosome', help='chromosome number')
    protein = fields.Char(
        'Protein involved', help='Name of the protein(s) affected')
    gene = fields.Char('Gene', help='Name of the gene(s) affected')
    information = fields.Text('Extra Info')

    active = fields.Boolean('Active', select=True)

    @classmethod
    def __setup__(cls):
        super(Disease, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('code_uniq', Unique(t, t.code), 'Disease code must be unique'),
        ]

    @staticmethod
    def default_active():
        return True

    def get_rec_name(self, name):
        return "%s : %s - %s" % (
            self.code, self.name, self.category and self.category.name or '')

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
            ('category.name', operator, value),
            ]
        return domain


class DiseaseMembers(ModelSQL, ModelView):
    'Disease group members'
    __name__ = 'galeno.disease.group.member'

    disease = fields.Many2One('galeno.disease', 'Disease',
        ondelete='CASCADE', required=True, select=True)
    group = fields.Many2One('galeno.disease.group', 'Group',
        ondelete='CASCADE', required=True, select=True)
