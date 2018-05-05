from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pyson import Bool, Eval, If
from trytond.transaction import Transaction
from trytond.pool import Pool
import trytond.tools as tools

import galeno_tools

__all__ = ['Patient', 'PatientDisability', 'PatientDisease', 'PatientVaccine',
    'PatientActivity', 'PatientDrug']


class Patient(ModelSQL, ModelView):
    'Patient'
    __name__ = 'galeno.patient'

    company = fields.Many2One('company.company', 'Company', required=True,
        states={
            'invisible': True,
        })
    code = fields.Char('Code', readonly=True)
    archive_number = fields.Char('Archive #',
        help="Physical folder number")
    fname = fields.Char('Names', required=True)
    lname = fields.Char('Surnames', required=True)
    name = fields.Char('Complete name', required=True,
        states={
            'invisible': True,
            'readonly': True,
        })
    identifier_type = fields.Selection(
        'get_identifier_type', 'Id. Type', required=True, sort=False)
    identifier = fields.Char('Identifier', required=True,
        help="Personal Identifier, Eg:CI/RUC")
    photo = fields.Binary('Photo', file_id='photo_id')
    photo_id = fields.Char('Photo ID',
        states={
            'invisible': True,
        })
    birthdate = fields.Date('Birthdate', required=True)
    age = fields.Function(fields.TimeDelta('Age'), 'on_change_with_age')
    age_char = fields.Function(fields.Char('Age'), 'on_change_with_age_char')
    country = fields.Many2One('country.country', 'Country', required=True,
        states={
            'readonly': True,
        })
    subdivision = fields.Many2One('country.subdivision', 'Subdivision',
        domain=[
            ('country', '=', Eval('country', -1)),
            ('parent', '=', None),
        ], depends=['country'], required=True)
    city = fields.Many2One('country.subdivision', 'City',
        domain=[
            ('parent', '=', Eval('subdivision', -1)),
        ], depends=['subdivision'])
    address = fields.Char('Address', required=True)
    email = fields.Char('e-mail', required=True)
    phone = fields.Char('Phone', required=True)
    emergency_phone = fields.Char('Emerg. Phone', help="Emergency Phone")
    gender = fields.Selection([
        (None, ''),
        ('male', 'Male'),
        ('female', 'Female')
    ], 'Gender', required=True)
    civil_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('windowed', 'Windowed'),
        ('divorced', 'Divorced'),
        ('concubinage', 'Concubinage'),
    ], 'Civil Status', required=True)
    laterality = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('ambidextrous', 'Ambidextrous'),
    ], 'Laterality')
    blood_type = fields.Selection([
        ('a-', 'A -'),
        ('a+', 'A +'),
        ('a-', 'AB -'),
        ('ab+', 'AB +'),
        ('b-', 'B -'),
        ('b+', 'B +'),
        ('o-', 'O -'),
        ('o+', 'O +'),
    ], 'Blood Type', required=True)
    religion = fields.Char('Religion')
    education_level = fields.Selection([
        (None, 'Nothing'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('bachelor', 'Bachelor'),
        ('university', 'University'),
        ('postgraduate', 'Postgraduate'),
    ], 'Education level', sort=False)
    occupation = fields.Many2One('galeno.occupation', 'Occupation')
    ethnic_group = fields.Many2One('galeno.ethnic.group', 'Ethnic Group')
    disability = fields.Boolean('Disability')
    disabilities = fields.One2Many(
        'galeno.patient.disability', 'patient', 'Disabilities',
        states={
            'invisible': ~Eval('disability')
        },
        depends=['patient'])
    diseases = fields.One2Many(
        'galeno.patient.disease', 'patient', 'Diseases',
        states={
            'readonly': False,
        })
    vaccines = fields.One2Many('galeno.patient.vaccine', 'patient', 'Vaccines')
    activities = fields.One2Many(
        'galeno.patient.activity', 'patient', 'Activities',
        help="List of sport activities")
    diet_type = fields.Selection(
        [
            (None, 'None'),
            ('omnivorous', 'Omnivorous'),
            ('carnivorous', 'Carnivorous'),
            ('vegetarian', 'Vegetarian')
        ], 'Diet type', sort=False)
    diet_type_note = fields.Text('Diet type note')
    meals_number = fields.Integer('Meals per day',
        domain=[
            If(Bool(Eval('meals_number')),
                ('meals_number', '>=', 1),
               ())
        ], help="Sleep hours per day")
    coffe_consumption = fields.Boolean('Coffe consumtion')
    sugar_consumption = fields.Boolean('Sugar consumtion')
    salt_consumption = fields.Boolean('Salt consumtion')
    feeding_notes = fields.Text('Feeding notes')
    sleep_time = fields.Integer('Sleep time',
        domain=[
            If(Bool(Eval('sleep_time')),
               [
                   ('sleep_time', '>=', 1),
                   ('sleep_time', '<=', 24)],
               [()])
        ], help="Sleep hours per day")
    sleep_notes = fields.Text('Sleep notes')
    drugs = fields.One2Many(
        'galeno.patient.drug', 'patient', 'Drugs',
        help="List of drug consumption")
    intersex = fields.Boolean('Intersex')
    sexual_orientation = fields.Selection(
        [
            ('gay', 'Gay'),
            ('lesbian', 'Lesbian'),
            ('straight', 'Straight'),
            ('unknown', 'Unknown'),
        ], 'Sexual orientation', sort=False)
    sexual_active = fields.Boolean('Sexual active')
    relation_type = fields.Selection(
        [
            (None, 'None'),
            ('monogamous', 'Monogamous'),
            ('polygamous', 'Polygamous'),
        ], 'Relation type',
        states={
            'invisible': ~Bool(Eval('sexual_active')),
            'required': Bool(Eval('sexual_active')),
        }, depends=['sexual_active'], sort=False)

    @classmethod
    def __setup__(cls):
        super(Patient, cls).__setup__()
        t = cls.__table__()
        cls._error_messages.update({
                'invalid_identifier': ('Invalid identifier "%(identifier)s" '
                    'on Patient "%(patient)s".'),
                'invalid_phone': ('Invalid phone "%(phone)s"'),
                'invalid_email': ('Invalid email "%(email)s"'),
                })
        cls._sql_constraints += [
            ('identifier_uniq', Unique(t, t.company, t.identifier),
             'Identifier must be unique'),
        ]

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @classmethod
    def default_country(cls):
        context = Transaction().context
        if context.get('country'):
            pool = Pool()
            Country = pool.get('country.country')
            country = Country(context.get('country'))
            return country.id
        return None

    @staticmethod
    def default_disability():
        return False

    @staticmethod
    def default_laterality():
        return 'right'

    @staticmethod
    def default_sexual_orientation():
        return 'straight'

    @staticmethod
    def default_sexual_active():
        return False

    @fields.depends('lname', 'fname', 'name')
    def on_change_fname(self):
        lname = self.lname and self.lname or ''
        fname = self.fname and self.fname or ''
        self.name = '%s %s' % (lname, fname)

    @fields.depends('lname', 'fname', 'name')
    def on_change_lname(self):
        lname = self.lname and self.lname or ''
        fname = self.fname and self.fname or ''
        self.name = '%s %s' % (lname, fname)

    @fields.depends('gender', 'photo_id')
    def on_change_gender(self):
        if self.gender:
            if not self.photo_id:
                path = 'galeno/icons/%s_patient.png' % (self.gender)
                self.photo = fields.Binary.cast(
                    tools.file_open(path, mode='rb').read())

    @fields.depends('photo', 'gender', 'photo_id')
    def on_change_photo(self):
        if self.photo:
            self.photo = galeno_tools.create_thumbnail(self.photo)

    @fields.depends('birthdate')
    def on_change_with_age(self, name=None):
        if self.birthdate:
            Date = Pool().get('ir.date')
            diff = Date.today() - self.birthdate
            return diff
        return None

    @fields.depends('birthdate')
    def on_change_with_age_char(self, name=None):
        if self.birthdate:
            context = Transaction().context
            locale = context.get('language', 'en')
            return galeno_tools.age_in_words(self.birthdate, locale=locale)
        return ''

    @fields.depends('country')
    def get_identifier_type(self):
        if self.country:
            return galeno_tools.IDENTIFIERS.get(self.country.code, [])
        return []

    @fields.depends('identifier_type', 'identifier', 'name')
    def on_change_with_identifier(self):
        if self.identifier_type and self.identifier:
            compat = galeno_tools.compat_identifier(
                self.identifier_type, self.identifier)
            self.check_identifier()
            return compat

    @fields.depends('phone', 'country')
    def on_change_with_phone(self):
        if self.country and self.phone:
            self.check_phones(['phone'])
            return galeno_tools.format_phone(self.phone, self.country.code)

    @fields.depends('emergency_phone', 'country')
    def on_change_with_emergency_phone(self):
        if self.country and self.emergency_phone:
            self.check_phones(['emergency_phone'])
            return galeno_tools.format_phone(
                self.emergency_phone, self.country.code)

    @fields.depends('email')
    def on_change_with_email(self):
        if self.email:
            mail_address = galeno_tools.format_mail_address(self.email)
            self.check_email()
            return mail_address

    @fields.depends('disability')
    def on_change_disability(self):
        if not self.disability:
            self.disabilities = None

    @classmethod
    def search_rec_name(cls, name, clause):
        _, operator, value = clause
        if operator.startswith('!') or operator.startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        domain = [bool_op,
            ('name', operator, value),
            ('identifier', operator, value),
            ]
        return domain

    @classmethod
    def validate(cls, patients):
        super(Patient, cls).validate(patients)
        for patient in patients:
            patient.check_identifier()
            patient.check_phones()
            patient.check_email()

    def check_identifier(self):
        valid = galeno_tools.validate_identifier(
            self.identifier_type, self.identifier)
        if not valid:
            self.raise_user_error('invalid_identifier', {
                'identifier': self.identifier,
                'patient': self.name,
                })

    def check_phones(self, phones=['phone', 'emergency_phone']):
        for phone in phones:
            if getattr(self, phone):
                valid_phone = galeno_tools.validate_phone(
                    getattr(self, phone), self.country.code)
                if not valid_phone:
                    self.raise_user_error('invalid_phone', {
                        'phone': getattr(self, phone),
                        })

    def check_email(self):
        valid = galeno_tools.validate_mail_address(self.email)
        if not valid:
            self.raise_user_error('invalid_email', {
                'email': self.email,
                })

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
                        config.patient_sequence.id)
        return super(Patient, cls).create(vlist)


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
    disease = fields.Many2One('galeno.disease', 'Disease')
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


class PatientDisease(ModelSQL, ModelView):
    'Patient Disease'
    __name__ = 'galeno.patient.disease'

    patient = fields.Many2One(
        'galeno.patient', 'Patient', ondelete='CASCADE', required=True)
    disease = fields.Many2One(
        'galeno.disease', 'Disease', ondelete='RESTRICT', required=True)
    severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ], 'Severity', required=True, sort=False)
    date = fields.Date('Date')
    #  TODO: add evaluation
    contagious = fields.Boolean('Contagious')
    notes = fields.Text('Notes')

    @staticmethod
    def default_severity():
        return 'mild'

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    @staticmethod
    def default_contagious():
        return False


class PatientVaccine(ModelSQL, ModelView):
    'Patient Vaccine'
    __name__ = 'galeno.patient.vaccine'

    patient = fields.Many2One(
        'galeno.patient', 'Patient', ondelete="CASCADE", required=True)
    vaccine = fields.Many2One(
        'galeno.vaccine', 'Vaccine', ondelete="RESTRICT", required=True)
    dose = fields.Integer('Dose',
        domain=[
            ('dose', '>', 0),
        ])
    route = fields.Selection([
        ('oral', 'Oral'),
        ('intramuscular', 'Intramuscular'),
        ('subcutaneous', 'Subcutaneous'),
        ('intradermal', 'Intradermal'),
        ('intranasal', 'Intranasal'),
    ], 'Route administration', required=True, sort=False)
    date = fields.Date('Date', required=True)
    next_date = fields.Date('Next Date')
    notes = fields.Text('Notes')

    @classmethod
    def __setup__(cls):
        super(PatientVaccine, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('vaccine_uniq', Unique(t, t.patient, t.vaccine, t.dose),
             'Vaccine dose must be unique per patient'),
        ]

    @staticmethod
    def default_dose():
        return 1


class PatientActivity(ModelSQL, ModelView):
    'Patient Activity'
    __name__ = 'galeno.patient.activity'

    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='CASCADE')
    activity = fields.Char('Activity', required=True)
    week_hours = fields.Integer('Week hours', required=True,
        domain=[
            ('week_hours', '>=', 1),
            ('week_hours', '<=', 56),
        ], help="Week time in hours, between 1 and 56")

    @staticmethod
    def default_week_hours():
        return 1

    def get_rec_name(self, name):
        return "%s - %s - %s" % (
            self.patient.rec_name, self.activity, self.week_hours)


class PatientDrug(ModelSQL, ModelView):
    'Patient Drug'
    __name__ = 'galeno.patient.drug'

    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='CASCADE')
    drug = fields.Many2One('galeno.drug', 'Drug', required=True)
    consume = fields.Boolean('Consume')
    consume_time = fields.Integer('Consume time',
        states={
            'invisible': ~Eval('consume'),
        },
        domain=[
            If(Bool(Eval('consume')),
               ('consume_time', '>=', 1),
               ())
        ], depends=['consume'], help="Time in months")
    consume_amount = fields.Integer('Consume Amount',
        states={
            'invisible': ~Eval('consume'),
        },
        domain=[
            If(Bool(Eval('consume')),
               ('consume_amount', '>=', 1),
               ())
        ], depends=['consume'], help="Amount per week")
    ex_consume = fields.Boolean('Ex consume')
    abstinence_time = fields.Integer('Abstinence time',
        states={
            'invisible': ~Eval('ex_consume'),
        },
        domain=[
            If(Bool(Eval('ex_consume')),
               ('abstinence_time', '>=', 3),
               ())
        ], depends=['ex_consume'],
        help="It is considered abstinence after three months")
    notes = fields.Text('Notes')
