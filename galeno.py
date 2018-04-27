from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.pool import Pool

from tools import (IDENTIFIERS, validate_identifier, compat_identifier,
    format_phone, validate_phone, age_in_words, create_thumbnail)
import trytond.tools as tryton_tools

__all__ = ['Patient']


class Patient(ModelSQL, ModelView):
    'Patient'
    __name__ = 'galeno.patient'

    company = fields.Many2One('company.company', 'Company', required=True,
        states={
            'invisible': True,
        })
    code = fields.Char('Code', readonly=True)
    archive_number = fields.Char('Archive #')
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
    ], 'Laterality', required=True)
    blood_type = fields.Selection([
        ('a-', 'a -'),
        ('a+', 'a +'),
        ('ab-', 'ab -'),
        ('ab+', 'ab +'),
        ('b-', 'b -'),
        ('b+', 'b +'),
        ('o-', 'o -'),
        ('o+', 'o +'),
    ], 'Blood Type', required=True)
    religion = fields.Char('Religion')
    education_level = fields.Selection([
        (None, 'Nothing'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('university', 'University'),
        ('postgraduate', 'Postgraduate'),
    ], 'Education level', sort=False)

    @classmethod
    def __setup__(cls):
        super(Patient, cls).__setup__()
        t = cls.__table__()
        cls._error_messages.update({
                'invalid_identifier': ('Invalid identifier "%(identifier)s" '
                    'on Patient "%(patient)s".'),
                'invalid_phone': ('Invalid phone "%(phone)s" '
                    'on Patient "%(patient)s".'),
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
        if self.gender and not self.photo_id:
            path = 'galeno/icons/%s_patient.png' % (self.gender)
            self.photo = fields.Binary.cast(
                tryton_tools.file_open(path, mode='rb').read())

    @fields.depends('photo')
    def on_change_photo(self):
        if self.photo:
            self.photo = create_thumbnail(self.photo)

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
            return age_in_words(self.birthdate, locale=locale)
        return ''

    @fields.depends('country')
    def get_identifier_type(self):
        if self.country:
            return IDENTIFIERS.get(self.country.code, [])

    @fields.depends('identifier_type', 'identifier', 'name')
    def on_change_with_identifier(self):
        if self.identifier_type and self.identifier:
            compat = compat_identifier(self.identifier_type, self.identifier)
            self.check_identifier()
            return compat

    @fields.depends('phone', 'country')
    def on_change_with_phone(self):
        if self.country and self.phone:
            return format_phone(self.phone, self.country.code)

    @fields.depends('emergency_phone', 'country')
    def on_change_with_emergency_phone(self):
        if self.country and self.emergency_phone:
            return format_phone(self.emergency_phone, self.country.code)

    @classmethod
    def validate(cls, patients):
        super(Patient, cls).validate(patients)
        for patient in patients:
            patient.check_identifier()

    def check_identifier(self):
        valid = validate_identifier(self.identifier_type, self.identifier)
        if not valid:
            self.raise_user_error('invalid_identifier', {
                'identifier': self.identifier,
                'patient': self.name,
                })

    def check_phones(self):
        phones = ['phone', 'emergency_phone']
        for phone in phones:
            if getattr(self, phone):
                valid_phone = validate_phone(
                    getattr(self, phone), self.country.code)
                if not valid_phone:
                    self.raise_user_error('invalid_phone', {
                        'phone': getattr(self, phone),
                        'patient': self.name,
                        })
