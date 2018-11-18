=================
Galeno Scenario
=================

Imports::
    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import Model, Wizard, Report
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()
    >>> from trytond.modules.galeno.tests.tools import create_country

Install galeno::
    >>> config = activate_modules(['country', 'galeno', 'galeno_base_data'])

Create company::
    >>> _ = create_company()
    >>> company = get_company()
    >>> company.timezone = 'America/Guayaquil'
    >>> company.save()

Create country::
    >>> country = create_country()
    >>> subdivision = country.subdivisions[0]
    >>> Subdivision = Model.get('country.subdivision')
    >>> city, = Subdivision.find([('parent', '=', subdivision.id)])

Select lang::
    >>> Lang = Model.get('ir.lang')
    >>> lang, = Lang.find(['code', '=', 'es'])

Add CIE10 data::
    >>> icd10 = Wizard('galeno.import.icd10')
    >>> icd10.form.language = lang
    >>> icd10.execute('import_icd10')

Add Professional::
    >>> Professional = Model.get('galeno.professional')
    >>> Speciality = Model.get('galeno.speciality')
    >>> speciality = Speciality.find([])
    >>> professional = Professional()
    >>> professional.name = 'Diego Abad'
    >>> professional.prefix = 'Dr.'
    >>> professional.speciality = speciality[0]
    >>> professional.medical_identifier = '0104488036'
    >>> professional.save()

Create Galeno user::
    >>> User = Model.get('res.user')
    >>> Group = Model.get('res.group')
    >>> Country = Model.get('country.country')
    >>> galeno_user = User()
    >>> galeno_user.name = 'Galeno'
    >>> galeno_user.login = 'galeno'
    >>> galeno_user.main_company = company
    >>> galeno_group, = Group.find([('name', '=', 'Galeno')])
    >>> galeno_user.groups.append(galeno_group)
    >>> galeno_user.professional = professional
    >>> galeno_user.country = country
    >>> galeno_user.main_company = company
    >>> galeno_user.company = company
    >>> galeno_user.save()

Create Basic Male Patient::
    >>> Patient = Model.get('galeno.patient')
    >>> patient_male_1 = Patient()
    >>> patient_male_1.fname = 'Juan Diego'
    >>> patient_male_1.lname = 'Castro Hernandez'
    >>> patient_male_1.identifier_type = 'ec.ci'
    >>> patient_male_1.identifier = '0104488036'
    >>> patient_male_1.gender = 'male'
    >>> patient_male_1.birthdate = datetime.date(year=1983, month=9, day=15)
    >>> patient_male_1.blood_type = 'o+'
    >>> patient_male_1.country = country
    >>> patient_male_1.subdivision = subdivision
    >>> patient_male_1.city = city
    >>> patient_male_1.civil_status = 'married'
    >>> patient_male_1.education_level = 'university'
    >>> patient_male_1.email = 'juan.castro@gmail.com'
    >>> patient_male_1.phone = '0992343221'
    >>> patient_male_1.address = 'Address 01'
    >>> patient_male_1.save()

Create Basic Female Patient::
    >>> Patient = Model.get('galeno.patient')
    >>> patient_female_1 = Patient()
    >>> patient_female_1.fname = 'Andrea Viviana'
    >>> patient_female_1.lname = 'Torres Jurado'
    >>> patient_female_1.identifier_type = 'ec.ci'
    >>> patient_female_1.identifier = '0104406848'
    >>> patient_female_1.gender = 'female'
    >>> patient_female_1.birthdate = datetime.date(year=2014, month=6, day=1)
    >>> patient_female_1.blood_type = 'o-'
    >>> patient_female_1.country = country
    >>> patient_female_1.subdivision = subdivision
    >>> patient_female_1.city = city
    >>> patient_female_1.civil_status = 'single'
    >>> patient_female_1.email = 'andrea.torres@gmail.com'
    >>> patient_female_1.phone = '0993234321'
    >>> patient_female_1.address = 'Address 01'
    >>> patient_female_1.save()

Create Female Patient with menarche info::
    >>> Patient = Model.get('galeno.patient')
    >>> patient_female_2 = Patient()
    >>> patient_female_2.fname = 'Diana Carolina'
    >>> patient_female_2.lname = 'Aguilar Delgado'
    >>> patient_female_2.identifier_type = 'ec.ci'
    >>> patient_female_2.identifier = '0104476189'
    >>> patient_female_2.gender = 'female'
    >>> patient_female_2.birthdate = datetime.date(year=1982, month=5, day=21)
    >>> patient_female_2.blood_type = 'o-'
    >>> patient_female_2.menarche = 13
    >>> patient_female_2.cycle_duration = 28
    >>> patient_female_2.cycle_type = 'regular'
    >>> patient_female_2.last_menstruation_date = (
    ...     today - relativedelta(months=-1))
    >>> patient_female_2.country = country
    >>> patient_female_2.subdivision = subdivision
    >>> patient_female_2.city = city
    >>> patient_female_2.civil_status = 'single'
    >>> patient_female_2.education_level = 'university'
    >>> patient_female_2.email = 'andrea.torres@gmail.com'
    >>> patient_female_2.phone = '0993234321'
    >>> patient_female_2.address = 'Address 01'
    >>> patient_female_2.save()
