from trytond.model import ModelView, ModelSQL, fields
from galeno_mixin import BasicMixin

__all__ = ['Drug']


class Drug(BasicMixin, ModelSQL, ModelView):
    'Drug'
    __name__ = 'galeno.drug'

    fill_required = fields.Boolean('Fill required')
