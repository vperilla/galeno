# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import user
from . import country
from . import occupation
from . import ethnic_group
from . import disease
from . import medicament
from . import vaccine
from . import drug
from . import patient
from . import configuration

__all__ = ['register']


def register():
    Pool.register(
        user.User,
        country.Subdivision,
        occupation.Occupation,
        ethnic_group.EthnicGroup,
        disease.DiseaseCategory,
        disease.DiseaseGroup,
        disease.Disease,
        disease.DiseaseMembers,
        medicament.Medicament,
        vaccine.Vaccine,
        drug.Drug,
        patient.Patient,
        patient.PatientDisability,
        patient.PatientDisease,
        patient.PatientVaccine,
        patient.PatientActivity,
        patient.PatientDrug,
        configuration.Configuration,
        module='galeno', type_='model')
    Pool.register(
        module='galeno', type_='wizard')
    Pool.register(
        module='galeno', type_='report')
