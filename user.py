from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['User']


class User(metaclass=PoolMeta):
    __name__ = 'res.user'

    country = fields.Many2One('country.country', 'Country')
    professional = fields.Many2One('galeno.professional', 'Professional')
    galeno_groups = fields.Many2Many(
        'galeno.group-related-res.user', 'user', 'group', 'Groups')

    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        cls._context_fields.insert(0, 'country')
        cls._context_fields.insert(1, 'professional')
        cls._context_fields.insert(1, 'galeno_groups')

    def get_status_bar(self, name):
        return self.name
