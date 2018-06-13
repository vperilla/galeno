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
from . import patient
from . import patient_background
from . import patient_appointment
from . import patient_evaluation
from . import patient_test
from . import patient_prescription
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
        patient_test.TestCategory,
        patient_test.Test,
        patient.Patient,
        patient.PatientPhoto,
        patient.PatientDisability,
        patient.PatientDisease,
        patient.PatientVaccine,
        patient.PatientActivity,
        patient.PatientDrug,
        patient_background.Medicament,
        patient_background.Disease,
        patient_background.Family,
        patient_background.Surgery,
        patient_appointment.PatientAppointment,
        patient_evaluation.PatientEvaluation,
        patient_evaluation.PatientEvaluationTest,
        patient_evaluation.PatientEvaluationDiagnosis,
        patient_evaluation.PatientEvaluationProcedure,
        patient_background.Test,
        patient_prescription.PatientPrescription,
        patient_prescription.PatientPrescriptionLine,
        configuration.Configuration,
        configuration.ConfigurationSequence,
        configuration.ConfigurationDuration,
        module='galeno', type_='model')
    Pool.register(
        module='galeno', type_='wizard')
    Pool.register(
        module='galeno', type_='report')
