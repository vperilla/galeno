from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.pyson import Eval
from trytond.pool import Pool
from trytond.modules.company.model import (
    CompanyMultiValueMixin, CompanyValueMixin)

__all__ = ['Configuration', 'ConfigurationSequence']


class Configuration(
        ModelSingleton, ModelSQL, ModelView, CompanyMultiValueMixin):
    'Galeno Configuration'
    __name__ = 'galeno.configuration'
    patient_sequence = fields.MultiValue(fields.Many2One(
        'ir.sequence', "Patient Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'galeno.patient'),
            ]))
    appointment_sequence = fields.MultiValue(fields.Many2One(
        'ir.sequence', "Appointment Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'galeno.patient.appointment'),
            ]))
    evaluation_sequence = fields.MultiValue(fields.Many2One(
        'ir.sequence', "Evaluation Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'galeno.patient.evaluation'),
            ]))
    request_test_sequence = fields.MultiValue(fields.Many2One(
        'ir.sequence', "Evaluation Request Test", required=True,
        domain=[
            ('company', 'in', [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'galeno.patient.evaluation.test'),
            ]))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field in ['patient_sequence', 'appointment_sequence',
                'evaluation_sequence', 'request_test_sequence']:
            return pool.get('galeno.configuration.sequence')
        return super(Configuration, cls).multivalue_model(field)

    @classmethod
    def default_patient_sequence(cls, **pattern):
        return cls.multivalue_model(
            'patient_sequence').default_patient_sequence()

    @classmethod
    def default_appointment_sequence(cls, **pattern):
        return cls.multivalue_model(
            'appointment_sequence').default_appointment_sequence()

    @classmethod
    def default_evaluation_sequence(cls, **pattern):
        return cls.multivalue_model(
            'evaluation_sequence').default_evaluation_sequence()

    @classmethod
    def default_request_test_sequence(cls, **pattern):
        return cls.multivalue_model(
            'request_test_sequence').default_request_test_sequence()


class ConfigurationSequence(ModelSQL, CompanyValueMixin):
    "Galeno Configuration Sequence"
    __name__ = 'galeno.configuration.sequence'
    patient_sequence = fields.Many2One(
        'ir.sequence', "Patient Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('company', -1), None]),
            ('code', '=', 'galeno.patient'),
            ],
        depends=['company'])
    appointment_sequence = fields.Many2One(
        'ir.sequence', "Appointment Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('company', -1), None]),
            ('code', '=', 'galeno.patient.appointment'),
            ],
        depends=['company'])
    evaluation_sequence = fields.Many2One(
        'ir.sequence', "Evaluation Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('company', -1), None]),
            ('code', '=', 'galeno.patient.evaluation'),
            ],
        depends=['company'])
    request_test_sequence = fields.Many2One(
        'ir.sequence', "Request Test Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('company', -1), None]),
            ('code', '=', 'galeno.patient.evaluation.test'),
            ],
        depends=['company'])

    @classmethod
    def default_patient_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('galeno', 'sequence_patient')
        except KeyError:
            return None

    @classmethod
    def default_appointment_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('galeno', 'sequence_patient_appointment')
        except KeyError:
            return None

    @classmethod
    def default_evaluation_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('galeno', 'sequence_patient_evaluation')
        except KeyError:
            return None

    @classmethod
    def default_request_test_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id(
                'galeno', 'sequence_patient_evaluation_test')
        except KeyError:
            return None
