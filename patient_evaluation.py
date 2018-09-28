from datetime import datetime
from decimal import Decimal

from sql.conditionals import Case

from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import Bool, Eval, If
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.tools import reduce_ids, grouped_slice
from trytond.config import config

from . import galeno_tools
from .galeno_mixin import GalenoShared

max_size = config.getint('galeno', 'max_attachment_size', default=5)

__all__ = ['PatientEvaluation', 'PatientEvaluationTest',
    'PatientEvaluationDiagnosis', 'PatientEvaluationProcedure',
    'PatientEvaluationImage']

_STATES = [
    ('initial', 'Initiated'),
    ('finish', 'Finished'),
    ('cancel', 'Canceled'),
]


class PatientEvaluation(GalenoShared, Workflow, ModelSQL, ModelView):
    'Patient Evaluation'
    __name__ = 'galeno.patient.evaluation'

    code = fields.Char('Code', readonly=True)
    start_date = fields.DateTime('Start Date', required=True,
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    end_date = fields.DateTime('End Date', readonly=True)
    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='RESTRICT',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'], select=True)
    patient_gender = fields.Function(
        fields.Selection([
            ('male', 'Male'),
            ('female', 'Female'),
        ], 'Gender'), 'on_change_with_patient_gender')
    patient_photo = fields.Function(
        fields.Binary('Photo'), 'on_change_with_patient_photo')
    patient_age = fields.Function(
        fields.Char('Age'), 'on_change_with_patient_age')
    reason = fields.Selection(
        [
            ('disease', 'Disease'),
            ('tracing', 'Tracing'),
            ('routine', 'Routine Exploration')
        ], 'Reason',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'], required=True, sort=False)
    reason_translated = reason.translated('reason')
    state = fields.Selection(_STATES, 'State', readonly=True, required=True)
    state_translated = state.translated('state')
    color = fields.Function(fields.Char('color'), 'get_color')
    symptoms = fields.Text('Illness symptoms',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    diagnostics = fields.One2Many(
        'galeno.patient.evaluation.diagnosis', 'evaluation', 'Diagnostics',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    procedures = fields.One2Many(
        'galeno.patient.evaluation.procedure', 'evaluation', 'Procedures',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    treatment = fields.Text('Treatment',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    # VITAL SIGNS
    systolic_pressure = fields.Float('Systolic Pressure (mm(hg))',
        domain=[
            If(Bool(Eval('systolic_pressure')),
               [
                   ('systolic_pressure', '>', 0),
                   ('systolic_pressure', '>', Eval('diastolic_pressure'))],
               [()])
        ],
        states={
            'readonly': ~Eval('state').in_(['initial']),
            'required': Bool(Eval('diastolic_pressure')),
        }, depends=['state', 'diastolic_pressure'])
    diastolic_pressure = fields.Float('Diastolic Pressure (mm(hg))',
        domain=[
            If(Bool(Eval('diastolic_pressure')),
               ('diastolic_pressure', '>', 0),
               ())
        ],
        states={
            'readonly': ~Eval('state').in_(['initial']),
            'required': Bool(Eval('systolic_pressure')),
        }, depends=['state', 'systolic_pressure'])
    temperature = fields.Float('Temperature (℃)',
        domain=[
            If(Bool(Eval('temperature')),
               ('temperature', '>', 0),
               ())
        ],
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'], help="% Celcius")
    heart_rate = fields.Float('Heart rate (b/m)',
        domain=[
            If(Bool(Eval('heart_rate')),
               ('heart_rate', '>', 0),
               ())
        ],
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    breathing_rate = fields.Float('Breathing rate (b/m)',
        domain=[
            If(Bool(Eval('breathing_rate')),
               ('breathing_rate', '>', 0),
               ())
        ],
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    oxygen_saturation = fields.Float('Oxygen saturation (%)',
        domain=[
            If(Bool(Eval('oxygen_saturation')),
               [
                   ('oxygen_saturation', '>', 0),
                   ('oxygen_saturation', '<', 1)],
               [()])
        ],
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'], help="% O2")
    weight = fields.Float('Weight (kg)',
        domain=[
            If(Bool(Eval('weight')),
               ('weight', '>', 0),
               ())
        ],
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'], help="Weight in Kg")
    heigth = fields.Float('Heigth (cm)',
        domain=[
            If(Bool(Eval('heigth')),
               ('heigth', '>', 0),
               ())
        ],
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'], help="Heigth in cm")
    bmi = fields.Function(
        fields.Float('BMI', digits=(16, 2)), 'on_change_with_bmi')
    hip = fields.Float('Hip (cm)    ',
        domain=[
            If(Bool(Eval('hip')),
               ('hip', '>', 0),
               ())
        ],
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'], help="in cm")
    waist = fields.Float('Waist (cm)',
        domain=[
            If(Bool(Eval('waist')),
               ('waist', '>', 0),
               ())
        ],
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'], help="in cm")
    whr = fields.Function(
        fields.Float('WHR', digits=(16, 2)), 'on_change_with_whr')
    malnutrition = fields.Boolean('Malnutrition',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    dehydration = fields.Boolean('Dehydration',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    # SYSTEMS - ORGANS
    so_respiratory = fields.Text('Respiratory',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    so_cardiovascular = fields.Text('Cardiovascular',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    so_digestive = fields.Text('Digestive',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    so_nervous = fields.Text('Nervous',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    so_sense = fields.Text('Sense',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    so_endocrine = fields.Text('Endocrine',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    so_skeletal_muscle = fields.Text('Skeletal - muscle',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    so_genitourinary = fields.Text('Genitourinary',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    so_hemolymphatic = fields.Text('Hemolymphatic',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    # REGIONAL PHYSICAL EXAMINATION
    rpe_skin_scars = fields.Boolean('Scars',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_skin_tatoo = fields.Boolean('Tatoo',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_skin_facer = fields.Boolean('Skin Facer',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_eyes_conjunctive = fields.Boolean('Conjunctive',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_eyes_pupils = fields.Boolean('Pupils',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_eyes_motility = fields.Boolean('Motility',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_ear_extern = fields.Boolean('Extern',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_ear_pavilion = fields.Boolean('Pavilion',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_ear_eardrums = fields.Boolean('Eardrums',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_oropharynx_lips = fields.Boolean('Lips',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_oropharynx_tongue = fields.Boolean('Tongue',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_oropharynx_pharynx = fields.Boolean('Pharynx',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_oropharynx_tonsils = fields.Boolean('Tonsils',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_oropharynx_teeth = fields.Boolean('Teeth',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_nose_partition = fields.Boolean('Partition',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_nose_turbinates = fields.Boolean('Turbinates',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_nose_mocous = fields.Boolean('Mocous',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_nose_paranasal_sinuses = fields.Boolean('Paranasal sinuses',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_neck_thyroid = fields.Boolean('Tyroid masses',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_neck_mobility = fields.Boolean('Mobility',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_chest_mammary_glands = fields.Boolean('Mammary glands',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_chest_heart = fields.Boolean('Heart',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_chest_lungs = fields.Boolean('Lungs',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_chest_ribs = fields.Boolean('Ribs',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_abdomen_viscera = fields.Boolean('Viscera',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_abdomen_abdominal_wall = fields.Boolean('Abdominal wall',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_column_flexibility = fields.Boolean('Flexibility',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_column_deviation = fields.Boolean('Deviation',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_column_pain = fields.Boolean('Pain',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_pelvis_pelvis = fields.Boolean('Pelvis',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_pelvis_genitals = fields.Boolean('Genitals',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_limbs_vascular = fields.Boolean('Vascular',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_limbs_superior = fields.Boolean('Superior limbs',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_limbs_inferior = fields.Boolean('Inferior limbs',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_neuro_strength = fields.Boolean('Strength',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_neuro_sensivity = fields.Boolean('Sensivity',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_neuro_march = fields.Boolean('March',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    rpe_notes = fields.Text('Notes',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    # MENTAL STATUS
    ms_eye = fields.Selection(
        [
            (None, None),
            ('1', 'No eye opening'),
            ('2', 'Eye opening in response to pain stimulus'),
            ('3', 'Eye opening to speech'),
            ('4', 'Eyes opening spontaneously'),
        ], 'Eye response', sort=False,
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_eye_translated = ms_eye.translated('ms_eye')
    ms_verbal = fields.Selection(
        [
            (None, None),
            ('1', 'No verbal response'),
            ('2', 'Incomprehensible sounds'),
            ('3', 'Inappropriate words'),
            ('4', 'Confused'),
            ('5', 'Oriented'),
        ], 'Verbal response', sort=False,
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_verbal_translated = ms_verbal.translated('ms_verbal')
    ms_motor = fields.Selection(
        [
            (None, None),
            ('1', 'No motor response'),
            ('2', 'Decerebrate posturing'),
            ('3', 'Decorticate posturing'),
            ('4', 'Withdrawal from pain'),
            ('5', 'Localizes to pain'),
            ('6', 'Obeys commands'),
        ], 'Motor response', sort=False,
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_motor_translated = ms_motor.translated('ms_motor')
    ms_glasgow_score = fields.Function(fields.Integer('Glasgow score',
        help="Glasgow Score: < 9 severe, 9 -12 moderate, > 13 minor"),
        'on_change_with_ms_glasgow_score')
    ms_violent_behavior = fields.Boolean('Violent behavior',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_orientation = fields.Boolean('Orientation',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_perception_reality = fields.Boolean('Perception reality',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_abstraction = fields.Boolean('Abstraction',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_calc_skill = fields.Boolean('Calculation skills',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_mood = fields.Selection(
        [
            ('normal', 'Normal'),
            ('sad', 'Sad'),
            ('angry', 'Angry'),
            ('happy', 'Happy'),
            ('disgusted', 'Disgusted'),
            ('euphoric', 'Euphoric'),
            ('apathetic', 'Apathetic'),
        ], 'Mood', sort=False,
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_mood_translated = ms_mood.translated('ms_mood')
    ms_memory = fields.Boolean('Memory',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_discernment = fields.Boolean('Discernment',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_vocabulary = fields.Boolean('Vocabulary',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_object_recognition = fields.Boolean('Object recognition',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    ms_notes = fields.Text('Notes',
        states={
            'readonly': ~Eval('state').in_(['initial']),
        }, depends=['state'])
    # REQUESTED TESTS
    requested_tests = fields.One2Many(
        'galeno.patient.evaluation.test', 'evaluation', 'Tests',
        states={
            'readonly': ~Bool(Eval('patient')) | ~Eval('state').in_(
                ['initial']),
        })
    images = fields.One2Many(
        'galeno.patient.evaluation.image', 'evaluation', 'Images', size=4,
        states={
            'readonly': ~Bool(Eval('patient')) | ~Eval('state').in_(
                ['initial']),
        })

    @classmethod
    def __setup__(cls):
        super(PatientEvaluation, cls).__setup__()
        cls._order = [
            ('start_date', 'DESC'),
            ('id', 'DESC'),
            ]
        cls._transitions |= set((
                ('initial', 'finish'),
                ('initial', 'cancel'),
                ('finish', 'initial'),
                ('cancel', 'initial'),
                ))
        cls._buttons.update({
                'cancel': {
                    'invisible': ~Eval('state').in_(['initial']),
                    'icon': 'tryton-cancel',
                    'depends': ['state'],
                    },
                'finish': {
                    'invisible': ~Eval('state').in_(['initial']),
                    'icon': 'tryton-ok',
                    'depends': ['state'],
                    },
                'initial': {
                    'invisible': Eval('state').in_(['initial']),
                    'icon': 'tryton-undo',
                    'depends': ['state'],
                    },
                })

    @staticmethod
    def default_state():
        return 'initial'

    @staticmethod
    def default_reason():
        return 'disease'

    @staticmethod
    def default_start_date():
        return datetime.now()

    @staticmethod
    def default_ms_mood():
        return 'normal'

    @classmethod
    def get_color(cls, evaluations, name):
        cursor = Transaction().connection.cursor()
        table = cls.__table__()
        result = {}

        ids = [e.id for e in evaluations]
        for sub_ids in grouped_slice(ids):
            red_sql = reduce_ids(table.id, sub_ids)
            query = table.select(
                table.id,
                Case(
                    (table.state == 'initial', 'khaki'),
                    (table.state == 'finish', 'lightgreen'),
                    else_='lightcoral'),
                where=red_sql,
            )
            cursor.execute(*query)
            result.update(dict(cursor.fetchall()))
        return result

    @fields.depends('patient')
    def on_change_with_patient_gender(self, name=None):
        if self.patient:
            return self.patient.gender
        return None

    @fields.depends('patient')
    def on_change_with_patient_photo(self, name=None):
        if self.patient:
            return fields.Binary.cast(self.patient.photo)
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
            bmi = Decimal(self.weight) / Decimal(((self.heigth / 100.0) ** 2))
            return bmi.quantize(Decimal('0.01'))
        return 0

    @fields.depends('hip', 'waist')
    def on_change_with_whr(self, name=None):
        if self.hip and self.waist:
            whr = Decimal(self.waist) / Decimal(self.hip)
            return whr.quantize(Decimal('0.01'))
        return 0

    @fields.depends('ms_eye', 'ms_verbal', 'ms_motor')
    def on_change_with_ms_glasgow_score(self, name=None):
        if self.ms_eye and self.ms_verbal and self.ms_motor:
            return int(self.ms_eye) + int(self.ms_verbal) + int(self.ms_motor)
        return None

    def get_rec_name(self, name):
        return "%s - %s" % (self.code, self.patient.rec_name)

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        domain = [bool_op,
            ('code',) + tuple(clause[1:]),
            ('patient',) + tuple(clause[1:]),
            ]
        return domain

    @classmethod
    @ModelView.button
    @Workflow.transition('initial')
    def initial(cls, evaluations):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('finish')
    def finish(cls, evaluations):
        for evaluation in evaluations:
            evaluation.end_date = datetime.now()
        cls.save(evaluations)

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, evaluations):
        for evaluation in evaluations:
            evaluation.end_date = datetime.now()
        cls.save(evaluations)

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Config = pool.get('galeno.configuration')

        vlist = [x.copy() for x in vlist]
        config = Config(1)
        for values in vlist:
            if values.get('code') is None:
                values['code'] = Sequence.get_id(
                        config.get_multivalue('evaluation_sequence').id)
        return super(PatientEvaluation, cls).create(vlist)


class PatientEvaluationTest(ModelSQL, ModelView):
    'Patient Evaluation Test'
    __name__ = 'galeno.patient.evaluation.test'
    _rec_name = 'code'

    code = fields.Char('Code', readonly=True)
    evaluation = fields.Many2One('galeno.patient.evaluation', 'Evaluation',
        ondelete='CASCADE', required=True,
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])
    evaluation_state = fields.Function(
        fields.Selection(_STATES, 'Evaluation state'),
        'on_change_with_evaluation_state')
    patient_gender = fields.Function(
        fields.Char('Patient gender',
            states={
                'invisible': True,
            }), 'on_change_with_patient_gender')
    test = fields.Many2One('galeno.test', 'Test',
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        },
        domain=['OR',
                ('gender', '=', Eval('patient_gender')),
                ('gender', '=', 'unisex'),
        ], depends=['patient_gender', 'evaluation_state'], required=True)
    request_date = fields.Date('Request Date',
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
            'required': True,
        }, depends=['evaluation_state'])
    reason = fields.Text('Reason',
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])
    with_result = fields.Boolean('With result',
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])
    result_date = fields.Date('Result Date',
        states={
            'readonly': ~Eval('with_result') | ~Eval(
                'evaluation_state').in_(['initial']),
            'required': Bool(Eval('with_result')),
        }, depends=['with_result', 'evaluation_state'])
    result_notes = fields.Text('Result',
        states={
            'readonly': ~Eval('with_result') | ~Eval(
                'evaluation_state').in_(['initial']),
        }, depends=['with_result', 'evaluation_state'])
    result_data = fields.Binary('Result data', file_id='file_id',
        filename='filename', help="Load result data, Ex: image",
        states={
            'readonly': ~Eval('with_result') | ~Eval(
                'evaluation_state').in_(['initial']),
        }, depends=['with_result', 'evaluation_state'])
    file_id = fields.Char('File ID')
    filename = fields.Char('Filename')

    @classmethod
    def __setup__(cls):
        super(PatientEvaluationTest, cls).__setup__()
        cls._error_messages.update({
                'invalid_size': ('Max size for results is %(max_size)s MB, '
                    'your attachment size has %(size)sMB'),
                })

    @staticmethod
    def default_request_date():
        Date = Pool().get('ir.date')
        return Date.today()

    @fields.depends('evaluation')
    def on_change_with_patient_gender(self, name=None):
        if self.evaluation:
            return self.evaluation.patient.gender
        return None

    @fields.depends('evaluation', '_parent_evaluation.state')
    def on_change_with_evaluation_state(self, name=None):
        if self.evaluation:
            return self.evaluation.state
        return None

    def get_rec_name(self, name):
        return "%s - %s" % (self.code, self.evaluation.patient.rec_name)

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        domain = [bool_op,
            ('code',) + tuple(clause[1:]),
            ('evaluation',) + tuple(clause[1:]),
            ]
        return domain

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Config = pool.get('galeno.configuration')

        vlist = [x.copy() for x in vlist]
        config = Config(1)
        for values in vlist:
            if values.get('code') is None:
                values['code'] = Sequence.get_id(
                        config.get_multivalue('request_test_sequence').id)
        return super(PatientEvaluationTest, cls).create(vlist)

    @classmethod
    def validate(cls, tests):
        super(PatientEvaluationTest, cls).validate(tests)
        cls.check_size(tests)

    @classmethod
    def check_size(cls, tests):
        for test in tests:
            if test.result_data:
                size = len(test.result_data) / (1000 * 1000)
                if size > max_size:
                    cls.raise_user_error('invalid_size', {
                        'size': int(size),
                        'max_size': max_size,
                        })

    @classmethod
    def search(cls, args, offset=0, limit=None, order=None, count=False,
            query=False):
        args = args[:]
        context = Transaction().context
        if context.get('galeno_group_filter'):
            args = ['AND', ('evaluation.galeno_group', '=',
                context['galeno_group_filter']), args[:]]
        if context.get('professional_filter'):
            args = ['AND', ('evaluation.professional', '=',
                context['professional_filter']), args[:]]
        return super(PatientEvaluationTest, cls).search(args, offset=offset,
            limit=limit, order=order, count=count, query=query)


class PatientEvaluationDiagnosis(ModelSQL, ModelView):
    'Patient Evaluation Diagnosis'
    __name__ = 'galeno.patient.evaluation.diagnosis'

    evaluation = fields.Many2One('galeno.patient.evaluation', 'Evaluation',
        ondelete='CASCADE', required=True)
    evaluation_state = fields.Function(
        fields.Selection(_STATES, 'Evaluation State'),
        'on_change_with_evaluation_state')
    disease = fields.Many2One('galeno.disease', 'Disease', required=True,
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])
    type_ = fields.Selection(
        [
            ('presumptive', 'Presumptive'),
            ('definitive', 'Definitive'),
        ], 'Type', required=True,
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])
    type_translated = type_.translated('type_')
    date = fields.Date('Date',
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])
    severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ], 'Severity', required=True, sort=False,
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])
    severity_translated = severity.translated('severity')
    contagious = fields.Boolean('Contagious',
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])
    notes = fields.Text('Notes',
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])

    @staticmethod
    def default_severity():
        return 'mild'

    @staticmethod
    def default_contagious():
        return False

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    @fields.depends('evaluation', '_parent_evaluation.state')
    def on_change_with_evaluation_state(self, name=None):
        if self.evaluation:
            return self.evaluation.state
        return None


class PatientEvaluationProcedure(ModelSQL, ModelView):
    'Patient Evaluation Procedure'
    __name__ = 'galeno.patient.evaluation.procedure'

    evaluation = fields.Many2One('galeno.patient.evaluation', 'Evaluation',
        ondelete='CASCADE', required=True)
    evaluation_state = fields.Function(
        fields.Selection(_STATES, 'Evaluation State'),
        'on_change_with_evaluation_state')
    procedure = fields.Many2One('galeno.procedure', 'Procedure', required=True,
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])
    date = fields.Date('Date', required=True,
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])
    notes = fields.Text('Notes',
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])

    @fields.depends('evaluation', '_parent_evaluation.state')
    def on_change_with_evaluation_state(self, name=None):
        if self.evaluation:
            return self.evaluation.state
        return None


class PatientEvaluationImage(ModelSQL, ModelView):
    'Patient Evaluation Image'
    __name__ = 'galeno.patient.evaluation.image'

    evaluation = fields.Many2One('galeno.patient.evaluation', 'Evaluation',
        ondelete='CASCADE', required=True)
    evaluation_state = fields.Function(
        fields.Selection(_STATES, 'Evaluation State'),
        'on_change_with_evaluation_state')
    image = fields.Binary('Image', file_id='image_id', filename='filename',
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state', 'image_id', 'filename'])
    filename = fields.Char('Filename')
    image_id = fields.Char('File ID')
    thumbnail = fields.Binary(
        'Thumbnail', file_id='thumbnail_id', depends=['thumbnail_id'])
    thumbnail_id = fields.Char('File ID')
    notes = fields.Text('Notes',
        states={
            'readonly': ~Eval('evaluation_state').in_(['initial']),
        }, depends=['evaluation_state'])

    @fields.depends('evaluation', '_parent_evaluation.state')
    def on_change_with_evaluation_state(self, name=None):
        if self.evaluation:
            return self.evaluation.state
        return None

    @fields.depends('image', 'thumbnail')
    def on_change_image(self):
        if self.image:
            self.image = galeno_tools.resize_image(self.image, (1280, 1024))
            self.thumbnail = galeno_tools.resize_image(self.image)
        else:
            self.thumbnail = None
