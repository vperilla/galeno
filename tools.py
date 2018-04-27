import pendulum

import stdnum.ec.ci as ci
import stdnum.ec.ruc as ruc

import phonenumbers
from phonenumbers import PhoneNumberFormat

from io import BytesIO
from PIL import Image

from trytond.model import fields

IDENTIFIERS = {
    'EC': [
        ('ec.ci', 'CI'),
        ('ec.ruc', 'RUC'),
        ('ec.passport', 'Passport')
    ],
}


def compat_identifier(type_, identifier):
    if type_ == 'ec.ci':
        validator = ci
    elif type_ == 'ec.ruc':
        validator = ruc
    elif type_ == 'ec.passport':
        return identifier
    else:
        pass
    try:
        return validator.compact(identifier)
    except Exception() as e:
        pass
    return identifier


def validate_identifier(type_, identifier):
    if type_ == 'ec.ci':
        validator = ci
    elif type_ == 'ec.ruc':
        validator = ruc
    elif type_ == 'ec.passport':
        return True
    else:
        pass
    try:
        if validator.is_valid(identifier):
            return True
        else:
            return False
    except Exception() as e:
        return False


def format_phone(number, country_code):
    try:
        x = phonenumbers.parse(number, country_code)
        return phonenumbers.format_number(x, PhoneNumberFormat.NATIONAL)
    except Exception() as e:
        pass
    return number


def validate_phone(number, country_code):
    try:
        x = phonenumbers.parse(number, country_code)
        return phonenumbers.is_valid_number(x)
    except Exception() as e:
        return False


def age_in_words(start, end=None, locale='en'):
    if end is None:
        end = pendulum.today().date()
    period = pendulum.period(start, end)
    return period.in_words(locale)


def create_thumbnail(data, size=(250, 250)):
    image = Image.open(BytesIO(data))
    image.thumbnail(size, Image.ANTIALIAS)
    result = BytesIO()
    image.save(result, image.format)
    return fields.Binary.cast(result.getvalue())
