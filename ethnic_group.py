from trytond.model import ModelView, ModelSQL
from galeno_mixin import BasicMixin

__all__ = ['EthnicGroup']


class EthnicGroup(BasicMixin, ModelSQL, ModelView):
    'Ethnic Group'
    __name__ = 'galeno.ethnic.group'
