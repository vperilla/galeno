from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pyson import Eval, If

__all__ = ['GalenoGroup', 'GalenoGroupRelatedUser']


class GalenoGroup(ModelSQL, ModelView):
    'Galeno Group'
    __name__ = 'galeno.group'

    name = fields.Char('Name', required=True)
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ], select=True)
    users = fields.Many2Many(
        'galeno.group-related-res.user', 'group', 'user', 'Users')

    @classmethod
    def __setup__(cls):
        super(GalenoGroup, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_uniq', Unique(t, t.name), 'Name must be unique !'),
        ]
        cls._order.insert(0, ('name', 'ASC'))


class GalenoGroupRelatedUser(ModelSQL):
    'Galeno Group - Related User'
    __name__ = 'galeno.group-related-res.user'
    _table = 'galeno_group_user_rel'
    group = fields.Many2One('galeno.group', 'Group',
        ondelete='CASCADE', select=True, required=True)
    user = fields.Many2One('res.user', 'User',
        ondelete='RESTRICT', select=True, required=True)
