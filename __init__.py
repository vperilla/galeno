# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import country
from . import occupation
from . import speciality
from . import professional
from . import user
from . import ethnic_group
from . import disease
from . import procedure
from . import medicament
from . import vaccine
from . import drug
from . import contraceptive_method
from . import test
from . import patient
from . import background
from . import evaluation
from . import prescription
from . import configuration

__all__ = ['register']


def register():
    Pool.register(
        country.Subdivision,
        occupation.Occupation,
        speciality.Speciality,
        professional.Professional,
        user.User,
        ethnic_group.EthnicGroup,
        disease.DiseaseCategory,
        disease.DiseaseGroup,
        disease.Disease,
        disease.DiseaseMembers,
        procedure.Procedure,
        medicament.Medicament,
        medicament.MedicamentDoseUnit,
        medicament.MedicamentFrequency,
        vaccine.Vaccine,
        drug.Drug,
        contraceptive_method.ContraceptiveMethod,
        test.TestCategory,
        test.Test,
        patient.Patient,
        patient.PatientPhoto,
        patient.PatientDisability,
        patient.PatientDisease,
        patient.PatientVaccine,
        patient.PatientActivity,
        patient.PatientDrug,
        background.Medicament,
        background.Disease,
        background.Family,
        background.Surgery,
        background.Test,
        evaluation.PatientEvaluation,
        evaluation.PatientEvaluationTest,
        evaluation.PatientEvaluationDiagnosis,
        evaluation.PatientEvaluationProcedure,
        prescription.PatientPrescription,
        prescription.PatientPrescriptionLine,
        configuration.Configuration,
        module='galeno', type_='model')
    Pool.register(
        module='galeno', type_='wizard')
    Pool.register(
        module='galeno', type_='report')
