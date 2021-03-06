from collections import defaultdict

from trytond.i18n import gettext
from trytond.model import ModelView, ModelSQL, fields, Unique, DeactivableMixin
from trytond.pyson import Bool, Eval, If, Id
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.tools import grouped_slice, reduce_ids, file_open
from trytond.exceptions import UserError

from . import galeno_tools

__all__ = ['Patient', 'PatientPhoto', 'PatientDisability', 'PatientVaccine',
    'PatientActivity', 'PatientDrug']


class Patient(DeactivableMixin, ModelSQL, ModelView):
    'Patient'
    __name__ = 'galeno.patient'
    # MAIN INFORMATION
    company = fields.Many2One('company.company', 'Company', required=True,
        states={
            'invisible': True,
        })
    code = fields.Char('Code', readonly=True)
    archive_number = fields.Char('Archive #',
        help="Physical folder number")
    fname = fields.Char('Names', required=True)
    lname = fields.Char('Surnames', required=True)
    identifier_type = fields.Selection(
        'get_identifier_type', 'Id. Type', required=True, sort=False)
    identifier = fields.Char('Identifier', required=True,
        help="Personal Identifier, Eg:CI/RUC")
    photo = fields.Function(
        fields.Binary('Photo'), 'get_photo', setter='set_photo')
    birthdate = fields.Date('Birthdate', required=True)
    age = fields.Function(fields.TimeDelta('Age'), 'on_change_with_age')
    age_char = fields.Function(fields.Char('Age'), 'on_change_with_age_char')
    nationality = fields.Many2One(
        'country.country', 'Nationality', required=True,
        states={
            'readonly': Bool(Eval('identifier_type') != 'passport')
        },
        domain=[
            If((Eval('identifier_type') != 'passport'),
               ('id', '=', Eval('country')),
               ())
        ], depends=['identifier_type', 'country'])
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
    work_place = fields.Char('Work Place')
    email = fields.Char('e-mail', required=True)
    phone = fields.Char('Phone', required=True,
        help="Phone with zone code, e.g. 072816912")
    emergency_phone = fields.Char('Emerg. Phone', help="Emergency Phone")
    gender = fields.Selection([
        (None, ''),
        ('male', 'Male'),
        ('female', 'Female')
    ], 'Gender', required=True)
    gender_translated = gender.translated('gender')
    # SECONDARY INFORMATION
    civil_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('divorced', 'Divorced'),
        ('concubinage', 'Concubinage'),
    ], 'Civil Status', required=True)
    civil_status_translated = civil_status.translated('civil_status')
    laterality = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('ambidextrous', 'Ambidextrous'),
    ], 'Laterality')
    laterality_translated = laterality.translated('laterality')
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
    allergies = fields.Char('Allergies')
    religion = fields.Char('Religion')
    education_level = fields.Selection([
        (None, 'Nothing'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('bachelor', 'Bachelor'),
        ('university', 'University'),
        ('postgraduate', 'Postgraduate'),
    ], 'Education level', sort=False)
    education_level_translated = education_level.translated('education_level')
    occupation = fields.Many2One('galeno.occupation', 'Occupation')
    ethnic_group = fields.Many2One('galeno.ethnic.group', 'Ethnic Group')
    disability = fields.Function(fields.Boolean('Disability'),
        'get_disability', searcher='search_disability')
    disabilities = fields.One2Many(
        'galeno.patient.disability', 'patient', 'Disabilities')
    # DISEASES
    diseases = fields.Function(
        fields.One2Many('galeno.patient.evaluation.diagnosis', None,
            'Diseases'), 'get_diseases')
    procedures = fields.Function(
        fields.One2Many('galeno.patient.evaluation.procedure', None,
            'Procedures'), 'get_procedures')
    # MEDICIDES - VACCINES
    pharma_lines = fields.Function(
        fields.One2Many('galeno.patient.prescription.pharma.line', None,
            'Medicaments'), 'get_medicaments')
    no_pharma_lines = fields.Function(
        fields.One2Many('galeno.patient.prescription.no.pharma.line', None,
            'No pharmamacological prescription'), 'get_medicaments')
    vaccines = fields.One2Many('galeno.patient.vaccine', 'patient', 'Vaccines')
    # LIFESTYLE
    # Diet
    diet_type = fields.Selection(
        [
            (None, 'None'),
            ('omnivorous', 'Omnivorous'),
            ('carnivorous', 'Carnivorous'),
            ('vegetarian', 'Vegetarian')
        ], 'Diet type', sort=False)
    diet_type_translated = diet_type.translated('diet_type')
    meals_number = fields.Integer('Meals per day',
        domain=['OR',
                ('meals_number', '=', None),
                ('meals_number', '>=', 0)
        ], help="Sleep hours per day")
    coffe_consumption = fields.Boolean('Coffe consumtion')
    sugar_consumption = fields.Boolean('Sugar consumtion')
    salt_consumption = fields.Boolean('Salt consumtion')
    feeding_notes = fields.Text('Feeding notes')
    # Activities
    activities = fields.One2Many(
        'galeno.patient.activity', 'patient', 'Activities',
        help="List of activities: sports, extra works and other activities")
    # Sleep
    sleep_time = fields.Integer('Sleep time in hours',
        domain=['OR',
            ('sleep_time', '=', None),
            [
                ('sleep_time', '>=', 0),
                ('sleep_time', '<=', 24)
            ]
        ], help="Sleep hours per day")
    sleep_in_day = fields.Boolean('Sleep in day')
    sleep_notes = fields.Text('Sleep notes')
    drugs = fields.One2Many(
        'galeno.patient.drug', 'patient', 'Drugs',
        help="List of drug consumption")
    # SEXUALITY
    intersex = fields.Boolean('Intersex')
    sexual_orientation = fields.Selection(
        [
            ('gay', 'Gay'),
            ('lesbian', 'Lesbian'),
            ('straight', 'Straight'),
            ('unknown', 'Unknown'),
        ], 'Sexual orientation', sort=False, required=True)
    sexual_orientation_translated = sexual_orientation.translated(
        'sexual_orientation')
    sexual_active = fields.Boolean('Sexual active')
    relation_type = fields.Selection(
        [
            (None, ''),
            ('none', 'None'),
            ('monogamous', 'Monogamous'),
            ('polygamous', 'Polygamous'),
        ], 'Relation type',
        states={
            'readonly': ~Bool(Eval('sexual_active')),
            'required': Bool(Eval('sexual_active')),
        }, depends=['sexual_active'], sort=False)
    relation_type_translated = relation_type.translated('relation_type')
    sexual_security = fields.Selection(
        [
            (None, ''),
            ('safe', 'Safe'),
            ('unsafe', 'Unsafe'),
        ], 'Sexual security',
        states={
            'readonly': ~Bool(Eval('sexual_active')),
            'required': Bool(Eval('sexual_active')),
        }, help="Security of sexual practices")
    sexual_security_translated = sexual_security.translated('sexual_security')
    contraceptive_method = fields.Many2One(
        'galeno.contraceptive.method', 'Contraceptive method',
        states={
            'readonly': ~Bool(Eval('sexual_active')),
        },
        domain=[['OR',
            ('gender', '=', Eval('gender')),
            ('gender', '=', 'unisex')]
        ], depends=['sexual_active', 'gender'])
    sexual_notes = fields.Text('Sexual notes')
    # BACKGROUNDS
    # Reproductive
    fertile = fields.Boolean('Fertile')
    menopause_andropause = fields.Boolean('Menopause / Andropause')
    menopause_andropause_age = fields.Integer('Menupause / Andropause age',
        states={
            'readonly': ~Bool(Eval('menopause_andropause')),
            'required': Bool(Eval('menopause_andropause')),
        },
        domain=[
            If(Bool(Eval('menopause_andropause')),
                ('menopause_andropause_age', '>=', 0),
               ())
        ], depends=['menopause_andropause', 'menopause_andropause_age'])
    menarche = fields.Integer('Menarche age',
        states={
            'invisible': Eval('gender') != 'female',
        },
        domain=[
            If((Eval('gender') == 'female') & Bool(Eval('menarche')),
                ('menarche', '>=', 0),
               ())
        ], depends=['gender'], help="Age of first menstruation")
    cycle_duration = fields.Integer('Cycle duration in days',
        states={
            'invisible': Eval('gender') != 'female',
            'readonly': ~Bool(Eval('menarche')),
            'required': Bool(Eval('menarche')),
        },
        domain=[
            If((Eval('gender') == 'female') & Bool(Eval('menarche')),
                ('cycle_duration', '>=', 0),
               ())
        ], depends=['gender', 'menarche'], help="Cycle duration in days")
    cycle_type = fields.Selection(
        [
            (None, 'None'),
            ('regular', 'Regular'),
            ('irregular', 'Irregular')
        ], 'Cycle Type',
        states={
            'invisible': Eval('gender') != 'female',
            'readonly': ~Bool(Eval('menarche')),
            'required': Bool(Eval('menarche')),
        }, sort=False)
    last_menstruation_date = fields.Date('Last menstruation date',
        states={
            'invisible': Eval('gender') != 'female',
            'readonly': ~Bool(Eval('menarche')),
            'required': Bool(Eval('menarche')),
        }, depends=['gender'])
    pregnancies = fields.Integer('Pregnancies',
        states={
            'invisible': Eval('gender') != 'female',
            'readonly': ~Bool(Eval('menarche')),
        },
        domain=[
            If(Eval('gender') == 'female',
                ('pregnancies', '>=', 0),
               ())
        ], depends=['gender'], help="Number of pregnancies of the patient")
    normal_labor = fields.Integer('Normal labor',
        states={
            'invisible': ~(Eval('gender') == 'female'),
            'readonly': ~Bool(Eval('pregnancies')),
            'required': Bool(Eval('pregnancies')),
        },
        domain=[
            If(Eval('gender') == 'female',
                ('normal_labor', '>=', 0),
               ())
        ], depends=['gender'])
    caesarean_labor = fields.Integer('Caesarean labor',
        states={
            'invisible': ~(Eval('gender') == 'female'),
            'readonly': ~Bool(Eval('pregnancies')),
            'required': Bool(Eval('pregnancies')),
        },
        domain=[
            If(Eval('gender') == 'female',
                ('caesarean_labor', '>=', 0),
               ())
        ], depends=['gender'])
    alive_children = fields.Integer('Alive children',
        domain=['OR',
            ('alive_children', '=', None),
            ('alive_children', '>=', 0),
        ])
    death_children = fields.Integer('Death children',
        domain=['OR',
            ('death_children', '=', None),
            ('death_children', '>=', 0),
        ], depends=['gender'])
    abortions = fields.Integer('Abortions',
        states={
            'invisible': ~(Eval('gender') == 'female'),
            'readonly': ~Bool(Eval('pregnancies')),
            'required': Bool(Eval('pregnancies')),
        },
        domain=[
            If(Eval('gender') == 'female',
                ('abortions', '>=', 0),
               ())
        ], depends=['gender'])
    actually_pregnant = fields.Boolean('Actually pregnant',
        states={
            'invisible': Eval('gender') != 'female',
        }, depends=['gender'])
    # BACKGROUNDS
    background_medicaments = fields.One2Many(
        'galeno.patient.background.medicament', 'patient',
        'Background Medicaments')
    background_diseases = fields.One2Many(
        'galeno.patient.background.disease', 'patient',
        'Background Diseases')
    background_family = fields.One2Many(
        'galeno.patient.background.family', 'patient',
        'Background Family')
    background_surgeries = fields.One2Many(
        'galeno.patient.background.surgery', 'patient',
        'Background Surgeries')
    background_tests = fields.One2Many(
        'galeno.patient.background.test', 'patient',
        'Background Tests')
    background_notes = fields.Text('Background Notes')

    @classmethod
    def __setup__(cls):
        super(Patient, cls).__setup__()
        t = cls.__table__()
        cls._buttons.update({
                'open_appointments': {
                    'icon': 'galeno-appointment',
                    },
                'open_evaluations': {
                    'icon': 'galeno-evaluation',
                    },
                'open_requested_tests': {
                    'icon': 'galeno-test',
                    },
                'open_prescriptions': {
                    'icon': 'galeno-prescription',
                    },
                })
        cls._sql_constraints += [
            ('identifier_uniq', Unique(t, t.company, t.identifier),
             'Identifier must be unique'),
        ]
        cls._order.insert(0, ('lname', 'ASC'))
        cls._order.insert(1, ('fname', 'ASC'))

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
    def default_laterality():
        return 'right'

    @staticmethod
    def default_sleep_in_day():
        return False

    @staticmethod
    def default_menopause_andropause():
        return False

    @staticmethod
    def default_sexual_orientation():
        return 'straight'

    @staticmethod
    def default_sexual_active():
        return False

    @staticmethod
    def default_cycle_duration():
        return 0

    @staticmethod
    def default_pregnancies():
        return 0

    @staticmethod
    def default_normal_labor():
        return 0

    @staticmethod
    def default_caesarean_labor():
        return 0

    @staticmethod
    def default_alive_children():
        return 0

    @staticmethod
    def default_death_children():
        return 0

    @staticmethod
    def default_abortions():
        return 0

    @staticmethod
    def default_actually_pregnant():
        return False

    @fields.depends('country', 'subdivision')
    def on_change_country(self):
        if self.country:
            self.nationality = self.country
        else:
            self.subdivision = None
            self.on_change_subdivision()

    @fields.depends('subdivision', 'city')
    def on_change_subdivision(self):
        if not self.subdivision:
            self.city = None

    @classmethod
    def get_photo(cls, patients, names):
        pool = Pool()
        PatientPhoto = pool.get('galeno.patient.photo')
        photos = {}
        for patient in patients:
            photo = PatientPhoto.search([('patient', '=', patient.id)])
            if photo:
                photos[patient.id] = fields.Binary.cast(photo[0].photo)
            else:
                path = 'galeno/icons/%s_patient.png' % (patient.gender)
                with file_open(path, mode='rb') as f:
                    photos[patient.id] = fields.Binary.cast(f.read())
        return {'photo': photos}

    @classmethod
    def set_photo(cls, patients, name, data):
        pool = Pool()
        PatientPhoto = pool.get('galeno.patient.photo')
        for patient in patients:
            photo = PatientPhoto.search([('patient', '=', patient.id)])
            if data:
                thumbnail = galeno_tools.resize_image(data)
                if photo:
                    photo = photo[0]
                    photo.photo = thumbnail
                else:
                    photo = PatientPhoto()
                    photo.patient = patient
                    photo.photo = thumbnail
                photo.save()
            else:
                PatientPhoto.delete(photo)

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

    @fields.depends('identifier_type', 'identifier')
    def on_change_with_identifier(self):
        if self.identifier_type and self.identifier:
            compat = galeno_tools.compat_identifier(
                self.identifier_type, self.identifier)
            self.check_identifier()
            return compat

    @fields.depends('email')
    def on_change_with_email(self):
        if self.email:
            mail_address = galeno_tools.format_mail_address(self.email)
            self.check_email()
            return mail_address

    @fields.depends('menarche', 'cycle_duration', 'cycle_type',
        'last_menstruation_date', 'pregnancies', 'normal_labor',
        'caesarean_labor', 'actually_pregnant')
    def on_change_menarche(self):
        if not self.menarche:
            self.cycle_duration = 0
            self.cycle_type = None
            self.last_menstruation_date = None
            self.pregnancies = 0
            self.normal_labor = 0
            self.caesarean_labor = 0
            self.actually_pregnant = 0

    @fields.depends('pregnancies', 'normal_labor', 'caesarean_labor')
    def on_change_pregnancies(self):
        if not self.pregnancies:
            self.normal_labor = 0
            self.caesarean_labor = 0

    @classmethod
    def get_disability(cls, patients, name):
        pool = Pool()
        patient = cls.__table__()
        Disability = pool.get('galeno.patient.disability')
        disability = Disability.__table__()
        cursor = Transaction().connection.cursor()
        result = defaultdict(lambda: False)
        ids = [p.id for p in patients]
        for sub_ids in grouped_slice(ids):
            red_sql = reduce_ids(patient.id, sub_ids)
            query = patient.join(disability,
                condition=patient.id == disability.patient
            ).select(
                patient.id,
                where=red_sql)
            cursor.execute(*query)
            for patient_id, in cursor.fetchall():
                result[patient_id] = True
        return result

    @classmethod
    def get_diseases(cls, patients, name):
        pool = Pool()
        patient = cls.__table__()
        Evaluation = pool.get('galeno.patient.evaluation')
        Diagnosis = pool.get('galeno.patient.evaluation.diagnosis')
        evaluation = Evaluation.__table__()
        diagnosis = Diagnosis.__table__()
        cursor = Transaction().connection.cursor()

        result = defaultdict(lambda: [])
        ids = [p.id for p in patients]
        for sub_ids in grouped_slice(ids):
            red_sql = reduce_ids(patient.id, sub_ids)
            query = patient.join(evaluation,
                condition=patient.id == evaluation.patient
            ).join(diagnosis,
                condition=evaluation.id == diagnosis.evaluation
            ).select(
                patient.id,
                diagnosis.id,
                where=red_sql & (evaluation.state == 'finish')
            )
            cursor.execute(*query)
            for patient_id, diagnosis_id in cursor.fetchall():
                result[patient_id].append(diagnosis_id)
        return result

    @classmethod
    def get_procedures(cls, patients, name):
        pool = Pool()
        patient = cls.__table__()
        Evaluation = pool.get('galeno.patient.evaluation')
        Procedure = pool.get('galeno.patient.evaluation.procedure')
        evaluation = Evaluation.__table__()
        procedure = Procedure.__table__()
        cursor = Transaction().connection.cursor()

        result = defaultdict(lambda: [])
        ids = [p.id for p in patients]
        for sub_ids in grouped_slice(ids):
            red_sql = reduce_ids(patient.id, sub_ids)
            query = patient.join(evaluation,
                condition=patient.id == evaluation.patient
            ).join(procedure,
                condition=evaluation.id == procedure.evaluation
            ).select(
                patient.id,
                procedure.id,
                where=red_sql & (evaluation.state == 'finish')
            )
            cursor.execute(*query)
            for patient_id, procedure_id in cursor.fetchall():
                result[patient_id].append(procedure_id)
        return result

    @classmethod
    def get_medicaments(cls, patients, names):
        pool = Pool()
        patient = cls.__table__()
        Prescription = pool.get('galeno.patient.prescription')
        PrescriptionLine = pool.get('galeno.patient.prescription.pharma.line')
        prescription = Prescription.__table__()
        prescription_line = PrescriptionLine.__table__()
        PrescriptionNoPharmaLine = pool.get(
            'galeno.patient.prescription.no.pharma.line')
        prescription_no_pharma_line = PrescriptionNoPharmaLine.__table__()
        cursor = Transaction().connection.cursor()

        pharma_lines = defaultdict(lambda: [])
        no_pharma_lines = defaultdict(lambda: [])
        ids = [p.id for p in patients]
        for sub_ids in grouped_slice(ids):
            red_sql = reduce_ids(patient.id, sub_ids)
            query = patient.join(prescription,
                condition=patient.id == prescription.patient
            ).join(prescription_line,
                condition=prescription.id == prescription_line.prescription
            ).select(
                patient.id,
                prescription_line.id,
                where=red_sql & (prescription.state == 'done')
            )
            cursor.execute(*query)
            for patient_id, line_id in cursor.fetchall():
                pharma_lines[patient_id].append(line_id)
            query = patient.join(prescription,
                condition=patient.id == prescription.patient
            ).join(prescription_no_pharma_line,
                condition=(
                    prescription.id == prescription_no_pharma_line.prescription)
            ).select(
                patient.id,
                prescription_no_pharma_line.id,
                where=red_sql & (prescription.state == 'done')
            )
            cursor.execute(*query)
            for patient_id, line_id in cursor.fetchall():
                no_pharma_lines[patient_id].append(line_id)

        return {
            'pharma_lines': pharma_lines,
            'no_pharma_lines': no_pharma_lines,
        }

    @classmethod
    def search_disability(cls, name, clause):
        pool = Pool()
        Disability = pool.get('galeno.patient.disability')
        disability = Disability.__table__()
        query = disability.select(disability.patient)
        operator = 'in' if clause[2] else 'not in'
        return [('id', operator, query)]

    def get_rec_name(self, name):
        return "%s %s" % (self.fname, self.lname)

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        domain = [bool_op,
            ('fname',) + tuple(clause[1:]),
            ('lname',) + tuple(clause[1:]),
            ]
        return domain

    @classmethod
    def validate(cls, patients):
        super(Patient, cls).validate(patients)
        for patient in patients:
            patient.check_identifier()
            patient.check_email()

    def check_identifier(self):
        valid = galeno_tools.validate_identifier(
            self.identifier_type, self.identifier)
        if not valid:
            raise UserError(
                gettext('galeno.invalid_identifier',
                identifier=self.identifier))

    def check_email(self):
        valid = galeno_tools.validate_mail_address(self.email)
        if not valid:
            raise UserError(
                gettext('galeno.invalid_email',
                email=self.email))

    @classmethod
    @ModelView.button_action('galeno.act_patient_appointments')
    def open_appointments(cls, patients):
        pass

    @classmethod
    @ModelView.button_action('galeno.act_patient_evaluations')
    def open_evaluations(cls, patients):
        pass

    @classmethod
    @ModelView.button_action('galeno.act_patient_requested_tests')
    def open_requested_tests(cls, patients):
        pass

    @classmethod
    @ModelView.button_action('galeno.act_patient_prescriptions')
    def open_prescriptions(cls, patients):
        pass

    @classmethod
    def view_attributes(cls):
        group_galeno = Id('galeno', 'group_galeno')
        return super(Patient, cls).view_attributes() + [
            ('/form/notebook/page[@id="patient_backgrounds"]', 'states', {
                    'invisible': ~(group_galeno).in_(
                        Eval('context', {}).get('groups', [])),
                    }),
            ('/form/notebook/page[@id="patient_lifestyle"]', 'states', {
                    'invisible': ~(group_galeno).in_(
                        Eval('context', {}).get('groups', [])),
                    }),
            ('/form/notebook/page[@id="patient_sexuality"]', 'states', {
                    'invisible': ~(group_galeno).in_(
                        Eval('context', {}).get('groups', [])),
                    }),
            ('/form/notebook/page[@id="patient_diseases"]', 'states', {
                    'invisible': ~(group_galeno).in_(
                        Eval('context', {}).get('groups', [])),
                    }),
            ('/form/notebook/page[@id="patient_procedures"]', 'states', {
                    'invisible': ~(group_galeno).in_(
                        Eval('context', {}).get('groups', [])),
                    }),
            ('/form/notebook/page[@id="patient_3"]', 'states', {
                    'invisible': ~(group_galeno).in_(
                        Eval('context', {}).get('groups', [])),
                    }),
            ]

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Config = pool.get('galeno.configuration')

        vlist = [x.copy() for x in vlist]
        config = Config(1)
        for values in vlist:
            if values.get('code') is None:
                values['code'] = Sequence.get_id(config.get_multivalue(
                    'patient_sequence').id)
        return super(Patient, cls).create(vlist)


class PatientPhoto(ModelSQL):
    'Patient Photo'
    __name__ = 'galeno.patient.photo'

    patient = fields.Many2One(
        'galeno.patient', 'Patient', required=True, ondelete='CASCADE')
    photo = fields.Binary('Photo', file_id='photo_id')
    photo_id = fields.Char('Photo ID')


class PatientDisability(ModelSQL, ModelView):
    'Patient Disability'
    __name__ = 'galeno.patient.disability'

    patient = fields.Many2One('galeno.patient', 'Patient', required=True,
        domain=[
            ('company', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ], ondelete='CASCADE')
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
    type_translated = type_.translated('type_')
    disease = fields.Many2One('galeno.disease', 'Disease')
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
    date = fields.Date('Date', required=True, help="Date of actual dosis")
    age_char = fields.Function(fields.Char('Age'), 'on_change_with_age_char')
    next_date = fields.Date('Next Date', help="Date of next dosis")
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

    @fields.depends('patient', 'date')
    def on_change_with_age_char(self, name=None):
        if self.date:
            context = Transaction().context
            locale = context.get('language', 'en')
            return galeno_tools.age_in_words(
                self.patient.birthdate, end=self.date, locale=locale)
        return ''


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
