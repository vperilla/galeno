from datetime import timedelta

from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.pyson import Eval
from trytond.pool import Pool
from trytond.modules.company.model import (
    CompanyMultiValueMixin, CompanyValueMixin)

__all__ = ['Configuration', 'ConfigurationSequence', 'ConfigurationDuration']


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
    evaluation_sequence = fields.MultiValue(fields.Many2One(
        'ir.sequence', "Evaluation Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'galeno.patient.evaluation'),
            ]))
    prescription_sequence = fields.MultiValue(fields.Many2One(
        'ir.sequence', "Prescription Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'galeno.patient.prescription'),
            ]))
    request_test_sequence = fields.MultiValue(fields.Many2One(
        'ir.sequence', "Evaluation Request Test", required=True,
        domain=[
            ('company', 'in', [Eval('context', {}).get('company', -1), None]),
            ('code', '=', 'galeno.patient.evaluation.test'),
            ]))
    attention_start = fields.MultiValue(
        fields.Time('Attention Start', required=True))
    attention_end = fields.MultiValue(
        fields.Time('Attention End', required=True))
    appointment_duration = fields.MultiValue(
        fields.TimeDelta('Appointment Duration', required=True))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field in ['patient_sequence', 'evaluation_sequence',
                'prescription_sequence', 'request_test_sequence']:
            return pool.get('galeno.configuration.sequence')
        elif field in ['attention_start', 'attention_end',
                'appointment_duration']:
            return pool.get('galeno.configuration.duration')
        return super(Configuration, cls).multivalue_model(field)

    @classmethod
    def default_patient_sequence(cls, **pattern):
        return cls.multivalue_model(
            'patient_sequence').default_patient_sequence()

    @classmethod
    def default_evaluation_sequence(cls, **pattern):
        return cls.multivalue_model(
            'evaluation_sequence').default_evaluation_sequence()

    @classmethod
    def default_prescription_sequence(cls, **pattern):
        return cls.multivalue_model(
            'prescription_sequence').default_prescription_sequence()

    @classmethod
    def default_request_test_sequence(cls, **pattern):
        return cls.multivalue_model(
            'request_test_sequence').default_request_test_sequence()

    @classmethod
    def default_appointment_duration(cls, **pattern):
        return cls.multivalue_model(
            'appointment_duration').default_appointment_duration()


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
    evaluation_sequence = fields.Many2One(
        'ir.sequence', "Evaluation Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('company', -1), None]),
            ('code', '=', 'galeno.patient.evaluation'),
            ],
        depends=['company'])
    prescription_sequence = fields.Many2One(
        'ir.sequence', "Evaluation Sequence", required=True,
        domain=[
            ('company', 'in', [Eval('company', -1), None]),
            ('code', '=', 'galeno.patient.prescription'),
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
    def default_evaluation_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('galeno', 'sequence_patient_evaluation')
        except KeyError:
            return None

    @classmethod
    def default_prescription_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('galeno', 'sequence_patient_prescription')
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


class ConfigurationDuration(ModelSQL, CompanyValueMixin):
    "Galeno Configuration Duration"
    __name__ = 'galeno.configuration.duration'

    attention_start = fields.Time('Attention Start', required=True)
    attention_end = fields.Time('Attention End', required=True)
    appointment_duration = fields.TimeDelta(
        'Appointment Duration', required=True)

    @staticmethod
    def default_appointment_duration():
        return timedelta(minutes=30)
