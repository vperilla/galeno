from trytond.model import ModelView, ModelSQL
from .galeno_mixin import BasicMixin

__all__ = ['Drug']


class Drug(BasicMixin, ModelSQL, ModelView):
    'Drug'
    __name__ = 'galeno.drug'
