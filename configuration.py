from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.pyson import Eval

__all__ = ['Configuration']


class Configuration(ModelSingleton, ModelSQL, ModelView):
    'Galeno Configuration'
    __name__ = 'galeno.configuration'
    patient_sequence = fields.Many2One(
        'ir.sequence', "Patient Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'galeno.patient'),
            ])
