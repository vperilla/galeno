# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import galeno

__all__ = ['register']


def register():
    Pool.register(
        galeno.Patient,
        module='galeno', type_='model')
    Pool.register(
        module='galeno', type_='wizard')
    Pool.register(
        module='galeno', type_='report')
