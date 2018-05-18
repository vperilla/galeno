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
    evaluation_sequence = fields.Many2One(
        'ir.sequence', "Evaluation Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'galeno.patient.evaluation'),
            ])
    request_test_sequence = fields.Many2One(
        'ir.sequence', "Evaluation Request Test", required=True,
        domain=[
            ('company', 'in', [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'galeno.patient.evaluation.test'),
            ])
