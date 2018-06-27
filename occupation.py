from trytond.model import ModelView, ModelSQL
from .galeno_mixin import BasicMixin

__all__ = ['Occupation']


class Occupation(BasicMixin, ModelSQL, ModelView):
    'Occupation'
    __name__ = 'galeno.occupation'
