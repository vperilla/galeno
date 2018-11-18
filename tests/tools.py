# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from proteus import Model

__all__ = ['create_country']


def create_country(config=None):
    "Create country data"
    Country = Model.get('country.country', config=config)
    Subdivision = Model.get('country.subdivision', config=config)

    country = Country(code='EC', code3='ECU', name='Ecuador',
        code_numeric='218')
    country.save()
    subdivision_1 = Subdivision(
        code='EC-A', name='Azuay', type='province', country=country)
    subdivision_1.save()
    city_1 = Subdivision(code='EC-A3', name='Cuenca', type='city',
        parent=subdivision_1, country=country)
    city_1.save()
    return country
