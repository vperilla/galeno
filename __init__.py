# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import user
from . import occupation
from . import ethnic_group
from . import disease
from . import patient
from . import medicament

__all__ = ['register']


def register():
    Pool.register(
        user.User,
        occupation.Occupation,
        ethnic_group.EthnicGroup,
        disease.DiseaseCategory,
        disease.DiseaseGroup,
        disease.Disease,
        disease.DiseaseMembers,
        patient.Patient,
        patient.PatientDisability,
        patient.PatientDisease,
        medicament.Medicament,
        module='galeno', type_='model')
    Pool.register(
        module='galeno', type_='wizard')
    Pool.register(
        module='galeno', type_='report')
