from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['User']


class User:
    __metaclass__ = PoolMeta
    __name__ = 'res.user'

    country = fields.Many2One('country.country', 'Country')

    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        cls._context_fields.insert(0, 'country')
