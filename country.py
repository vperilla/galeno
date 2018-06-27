from trytond.pool import PoolMeta

__all__ = ['Subdivision']


class Subdivision(metaclass=PoolMeta):
    __name__ = 'country.subdivision'

    @classmethod
    def __setup__(cls):
        super(Subdivision, cls).__setup__()
        cls._order.insert(0, ('name', 'ASC'))
