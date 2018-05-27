from trytond.model import ModelView, ModelSQL
from galeno_mixin import BasicMixin

__all__ = ['Speciality']


class Speciality(BasicMixin, ModelSQL, ModelView):
    'Speciality'
    __name__ = 'galeno.speciality'
