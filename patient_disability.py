from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, If

__all__ = ['PatientDisability']


class PatientDisability(ModelSQL, ModelView):
    'Patient Disability'
    __name__ = 'galeno.patient.disability'

    patient = fields.Many2One('galeno.patient', 'Patient', required=True,
        domain=[
            ('company', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ])
    type_ = fields.Selection(
        [
            ('hearing', 'Hearing'),
            ('physical', 'Physical'),
            ('intellectual', 'Intellectual'),
            ('language', 'Language'),
            ('mental', 'Mental'),
            ('psychological', 'Psycological'),
            ('psychosocial', 'Psychosocial'),
            ('visual', 'Visual'),
            ('other', 'Other'),
        ], 'Type', sort=False, required=True)
    disease = fields.Many2One('galeno.disease', 'Disease', required=True)
    start_date = fields.Date('Start date')
    legal_reference = fields.Char('Legal reference',
        help='legal document that verifies the authenticity of the condition')
    percentage = fields.Float('Percentage', required=True,
        domain=[
            ('percentage', '>=', 0),
            ('percentage', '<=', 1),
        ])
    description = fields.Text('Description')

    @staticmethod
    def default_percentage():
        return 0
