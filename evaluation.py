from datetime import datetime
from decimal import Decimal

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Bool, Eval, If
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.tools import reduce_ids, grouped_slice

import galeno_tools

__all__ = ['PatientEvaluation', 'PatientEvaluationTest']


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
    symptoms = fields.Text('Illness symptoms')
    treatment = fields.Text('Treatment')
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
    so_respiratory = fields.Text('Respiratory')
    so_cardiovascular = fields.Text('Cardiovascular')
    so_digestive = fields.Text('Digestive')
    so_nervous = fields.Text('Nervous')
    so_sense = fields.Text('Sense')
    so_endocrine = fields.Text('Endocrine')
    so_skeletal_muscle = fields.Text('Skeletal - muscle')
    so_geninourinary = fields.Text('Genitourinary')
    so_hemolymphatic = fields.Text('Hemolymphatic')
    # REGIONAL PHYSICAL EXAMINATION
    rpe_skin_scars = fields.Boolean('Scars')
    rpe_skin_tatoo = fields.Boolean('Tatoo')
    rpe_skin_facer = fields.Boolean('Skin Facer')
    rpe_eyes_conjunctive = fields.Boolean('Conjunctive')
    rpe_eyes_pupils = fields.Boolean('Pupils')
    rpe_eyes_motility = fields.Boolean('Motility')
    rpe_ear_extern = fields.Boolean('Extern')
    rpe_ear_pavilion = fields.Boolean('Pavilion')
    rpe_ear_eardrums = fields.Boolean('Eardrums')
    rpe_oropharynx_lips = fields.Boolean('Lips')
    rpe_oropharynx_tongue = fields.Boolean('Tongue')
    rpe_oropharynx_pharynx = fields.Boolean('Pharynx')
    rpe_oropharynx_tonsils = fields.Boolean('Tonsils')
    rpe_oropharynx_teeth = fields.Boolean('Teeth')
    rpe_nose_partition = fields.Boolean('Partition')
    rpe_nose_turbinates = fields.Boolean('Turbinates')
    rpe_nose_mocous = fields.Boolean('Mocous')
    rpe_nose_paranasal_sinuses = fields.Boolean('Paranasal sinuses')
    rpe_neck_thyroid = fields.Boolean('Tyroid masses')
    rpe_neck_mobility = fields.Boolean('Mobility')
    rpe_chest_mammary_glands = fields.Boolean('Mammary glands')
    rpe_chest_heart = fields.Boolean('Heart')
    rpe_chest_lungs = fields.Boolean('Lungs')
    rpe_chest_ribs = fields.Boolean('Ribs')
    rpe_abdomen_viscera = fields.Boolean('Viscera')
    rpe_abdomen_adbominal_wall = fields.Boolean('Abdominal wall')
    rpe_column_flexibility = fields.Boolean('Flexibility')
    rpe_column_deviation = fields.Boolean('Deviation')
    rpe_column_pain = fields.Boolean('Pain')
    rpe_pelvis_pelvis = fields.Boolean('Pelvis')
    rpe_pelvis_genitals = fields.Boolean('Genitals')
    rpe_limbs_vascular = fields.Boolean('Vascular')
    rpe_limbs_superior = fields.Boolean('Superior limbs')
    rpe_limbs_inferior = fields.Boolean('Inferior limbs')
    rpe_neuro_strength = fields.Boolean('Strength')
    rpe_neuro_sensivity = fields.Boolean('Sensivity')
    rpe_neuro_march = fields.Boolean('March')
    rpe_notes = fields.Text('Notes')
    # MENTAL STATUS
    ms_eye = fields.Selection(
        [
            ('1', 'No eye opening'),
            ('2', 'Eye opening in response to pain stimulus'),
            ('3', 'Eye opening to speech'),
            ('4', 'Eyes opening spontaneously'),
        ], 'Eye response', sort=False)
    ms_verbal = fields.Selection(
        [
            ('1', 'No verbal response'),
            ('2', 'Incomprehensible sounds'),
            ('3', 'Inappropriate words'),
            ('4', 'Confused'),
            ('5', 'Oriented'),
        ], 'Verbal response', sort=False)
    ms_motor = fields.Selection(
        [
            ('1', 'No motor response'),
            ('2', 'Decerebrate posturing'),
            ('3', 'Decorticate posturing'),
            ('4', 'Withdrawal from pain'),
            ('5', 'Localizes to pain'),
            ('6', 'Obeys commands'),
        ], 'Motor response', sort=False)
    ms_glasgow_score = fields.Function(fields.Integer('Glasgow score',
        help="Glasgow Score: < 9 severe, 9 -12 moderate, > 13 minor"),
        'on_change_with_ms_glasgow_score')
    ms_violent_behavior = fields.Boolean('Violent behavior')
    ms_orientation = fields.Boolean('Orientation')
    ms_percetption_reality = fields.Boolean('Perception reality')
    ms_abstraction = fields.Boolean('Abstraction')
    ms_calc_skill = fields.Boolean('Calculation skills')
    ms_mood = fields.Selection(
        [
            ('normal', 'Normal'),
            ('sad', 'Sad'),
            ('angry', 'Angry'),
            ('happy', 'Happy'),
            ('disgusted', 'Disgusted'),
            ('euphoric', 'Euphoric'),
            ('apathetic', 'Apathetic'),
        ], 'Mood', sort=False)
    ms_memory = fields.Boolean('Memory')
    ms_discernment = fields.Boolean('Discernment')
    ms_vocabulary = fields.Boolean('Vocabulary')
    ms_object_recognition = fields.Boolean('Object recognition')
    ms_notes = fields.Text('Notes')
    # REQUESTED TESTS
    requested_tests = fields.One2Many(
        'galeno.patient.evaluation.test', 'evaluation', 'Tests',
        states={
            'readonly': ~Eval('patient'),
        })

    @staticmethod
    def default_state():
        return 'progress'

    @staticmethod
    def default_start_date():
        return datetime.now()

    @staticmethod
    def default_mood():
        return 'normal'

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

    @fields.depends('ms_eye', 'ms_verbal', 'ms_motor')
    def on_change_with_ms_glasgow_score(self, name=None):
        if self.ms_eye and self.ms_verbal and self.ms_motor:
            return int(self.ms_eye) + int(self.ms_verbal) + int(self.ms_motor)
        return None


class PatientEvaluationTest(ModelSQL, ModelView):
    'Patient Evaluation Test'
    __name__ = 'galeno.patient.evaluation.test'

    evaluation = fields.Many2One('galeno.patient.evaluation', 'Evaluation',
        ondelete='CASCADE', required=True)
    patient = fields.Function(fields.Many2One('galeno.patient', 'Patient'),
        'get_patient', searcher='search_patient')
    patient_gender = fields.Function(
        fields.Char('Patient gender',
            states={
                'invisible': True,
            }), 'on_change_with_patient_gender')
    test = fields.Many2One('galeno.test', 'Test',
        domain=['OR',
                ('gender', '=', Eval('patient_gender')),
                ('gender', '=', 'unisex'),
        ], depends=['patient_gender'], required=True)
    reason = fields.Text('Reason', required=True)
    with_result = fields.Boolean('With result')
    result_date = fields.Date('Result Date',
        states={
            'readonly': ~Eval('with_result'),
        })
    result_notes = fields.Text('Result',
        states={
            'readonly': ~Eval('with_result'),
        })
    result_data = fields.Binary('Result data', file_id='file_id',
        filename='filename', help="Load result data, Ex: image",
        states={
            'readonly': ~Eval('with_result'),
        })
    file_id = fields.Char('File ID')
    filename = fields.Char('Filename')

    @classmethod
    def get_patient(cls, evaluation_tests, names):
        pool = Pool()
        cursor = Transaction().connection.cursor()
        Evaluation = pool.get('galeno.patient.evaluation')
        evaluation = Evaluation.__table__()
        eval_test = cls.__table__()
        patients = {}
        eval_ids = [e.id for e in evaluation_tests]
        for sub_ids in grouped_slice(eval_ids):
            where = reduce_ids(eval_test.id, sub_ids)
            query = eval_test.join(evaluation,
                condition=evaluation.id == eval_test.evaluation
            ).select(
                eval_test.id,
                evaluation.patient,
                where=where)
            cursor.execute(*query)
            patients.update(cursor.fetchall())
        return {
            'patient': patients
        }

    @classmethod
    def search_patient(cls, name, clause):
        return [('evaluation.' + clause[0],) + tuple(clause[1:])]

    @fields.depends('evaluation')
    def on_change_with_patient_gender(self, name=None):
        if self.evaluation:
            return self.evaluation.patient.gender
        return None
