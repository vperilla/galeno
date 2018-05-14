from datetime import datetime
from decimal import Decimal

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Bool, Eval, If
from trytond.transaction import Transaction

import galeno_tools

__all__ = ['PatientEvaluation']


class PatientEvaluation(ModelSQL, ModelView):
    'Patient Evaluation'
    __name__ = 'galeno.patient.evaluation'

    code = fields.Char('Code', readonly=True)
    start_date = fields.DateTime('Start Date', required=True)
    end_date = fields.DateTime('End Date', readonly=True)
    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='RESTRICT')
    patient_gender = fields.Function(
        fields.Selection([
            ('male', 'Male'),
            ('female', 'Female'),
        ], 'Gender'), 'on_change_with_patient_gender')
    patient_age = fields.Function(
        fields.Char('Age'), 'on_change_with_patient_age')
    reason = fields.Selection(
        [
            ('disease', 'Disease'),
            ('tracing', 'Tracing'),
            ('routine', 'Routine Exploration')
        ], 'Reason', required=True, sort=False)
    state = fields.Selection(
        [
            ('progress', 'Progress'),
            ('done', 'Done'),
        ], 'State', readonly=True, required=True)
    summary = fields.Text('Summary')
    # VITAL SIGNS
    systolic_pressure = fields.Float('Systolic Pressure',
        domain=[
            If(Bool(Eval('systolic_pressure')),
               ('systolic_pressure', '>', 0),
               ())
        ])
    diastolic_pressure = fields.Float('Diastlic Pressure',
        domain=[
            If(Bool(Eval('diastolic_pressure')),
               ('diastolic_pressure', '>', 0),
               ())
        ])
    temperature = fields.Float('Temperature',
        domain=[
            If(Bool(Eval('temperature')),
               ('temperature', '>', 0),
               ())
        ], help="% Celcius")
    heart_rate = fields.Float('Heart rate',
        domain=[
            If(Bool(Eval('heart_rate')),
               ('heart_rate', '>', 0),
               ())
        ])
    breathing_rate = fields.Float('Breathing rate',
        domain=[
            If(Bool(Eval('breathing_rate')),
               ('breathing_rate', '>', 0),
               ())
        ])
    oxygen_saturation = fields.Float('Oxygen saturation',
        domain=[
            If(Bool(Eval('oxygen_saturation')),
               ('oxygen_saturation', '>', 0),
               ())
        ], help="% O2")
    weight = fields.Float('Weight',
        domain=[
            If(Bool(Eval('weight')),
               ('weight', '>', 0),
               ())
        ], help="Weight in Kg")
    heigth = fields.Float('Heigth',
        domain=[
            If(Bool(Eval('heigth')),
               ('heigth', '>', 0),
               ())
        ], help="Heigth in cm")
    bmi = fields.Function(
        fields.Float('BMI', digits=(16, 2)), 'on_change_with_bmi')
    hip = fields.Float('Hip',
        domain=[
            If(Bool(Eval('hip')),
               ('hip', '>', 0),
               ())
        ], help="in cm")
    waist = fields.Float('Waist',
        domain=[
            If(Bool(Eval('waist')),
               ('waist', '>', 0),
               ())
        ], help="in cm")
    whr = fields.Function(
        fields.Float('WHR', digits=(16, 2)), 'on_change_with_whr')
    malnutrition = fields.Boolean('Malnutrition')
    dehydration = fields.Boolean('Dehydration')
    # SYSTEMS - ORGANS
    symptoms = fields.Text('Illness symptoms')
    so_respiratory = fields.Text('Respiratory')
    so_cardiovascular = fields.Text('Cardiovascular')
    so_digestive = fields.Text('Digestive')
    so_nervous = fields.Text('Nervous')
    so_sense = fields.Text('Sense')
    so_endocrine = fields.Text('Endocrine')
    so_skeletal_muscle = fields.Text('Skeletal - muscle')
    so_geninourinary = fields.Text('Genitourinary')
    so_hemolymphatic = fields.Text('Hemolymphatic')

    @staticmethod
    def default_state():
        return 'progress'

    @staticmethod
    def default_start_date():
        return datetime.now()

    @fields.depends('patient')
    def on_change_with_patient_gender(self, name=None):
        if self.patient:
            return self.patient.gender
        return None

    @fields.depends('patient', 'start_date')
    def on_change_with_patient_age(self, name=None):
        if self.patient and self.start_date:
            context = Transaction().context
            locale = context.get('language', 'en')
            return galeno_tools.age_in_words(self.patient.birthdate,
                end=self.start_date.date(), locale=locale)
        return ''

    @fields.depends('weight', 'heigth')
    def on_change_with_bmi(self, name=None):
        if self.weight and self.heigth:
            return Decimal(self.weight) / Decimal(((self.heigth / 100.0) ** 2))
        return 0

    @fields.depends('hip', 'waist')
    def on_change_with_whr(self, name=None):
        if self.hip and self.waist:
            return Decimal(self.waist) / Decimal(self.hip)
        return 0
