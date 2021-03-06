import pendulum
import pytz
from io import BytesIO

import stdnum.ec.ci as ci
import stdnum.ec.ruc as ruc

import phonenumbers
from phonenumbers import PhoneNumberFormat

from PIL import Image, ImageOps

from email_validator import validate_email

from trytond.model import fields

IDENTIFIERS = {
    'EC': [
        ('ec.ci', 'CI'),
        ('ec.ruc', 'RUC'),
        ('passport', 'Passport')
    ],
}


def compat_identifier(type_, identifier):
    if type_ == 'ec.ci':
        validator = ci
    elif type_ == 'ec.ruc':
        validator = ruc
    elif type_ == 'passport':
        return identifier
    else:
        pass
    try:
        return validator.compact(identifier)
    except Exception:
        pass
    return identifier


def validate_identifier(type_, identifier):
    if type_ == 'ec.ci':
        validator = ci
    elif type_ == 'ec.ruc':
        validator = ruc
    elif type_ == 'passport':
        return True
    else:
        pass
    try:
        if validator.is_valid(identifier):
            return True
        else:
            return False
    except Exception:
        return False


def format_phone(number, country_code):
    try:
        x = phonenumbers.parse(number, country_code)
        number = phonenumbers.format_number(x, PhoneNumberFormat.NATIONAL)
    except Exception:
        pass
    return number


def validate_phone(number, country_code):
    try:
        x = phonenumbers.parse(number, country_code)
        valid = phonenumbers.is_valid_number(x)
        if valid:
            return True
    except Exception:
        pass
    return False


def format_mail_address(email):
    try:
        v = validate_email(email)
        email = v['email']
    except Exception:
        pass
    return email


def validate_mail_address(email):
    try:
        validate_email(email)
        return True
    except Exception:
        pass
    return False


def age_in_words(start, end=None, locale='en'):
    if end is None:
        end = pendulum.today().date()
    period = pendulum.period(start, end)
    return period.in_words(locale)


def resize_image(data, size=(500, 500), fit=None):
    image = Image.open(BytesIO(data))
    image_format = image.format
    image_orientation = None
    if hasattr(image, '_getexif'):
        image_exif = image._getexif()
        if image_exif:
            image_orientation = image_exif.get(274)

    # Rotate depending on orientation.
    if image_orientation:
        if image_orientation == 3:
            image = image.rotate(180)
        elif image_orientation == 6:
            image = image.rotate(-90, expand=1)
        elif image_orientation == 8:
            image = image.rotate(90, expand=1)
    result = BytesIO()
    if fit is None:
        image.thumbnail(size, Image.ANTIALIAS)
    else:
        image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image.save(result, image_format)
    return fields.Binary.cast(result.getvalue())


def format_datetime(value, timezone='UTC', time_format='%x %X %Z'):
    if timezone not in pytz.all_timezones:
        timezone = 'UTC'
    tz = pytz.timezone(timezone)
    return pytz.UTC.localize(value).astimezone(tz).strftime(time_format)
