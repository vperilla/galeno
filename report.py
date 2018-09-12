from io import BytesIO

from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.company import CompanyReport

from .galeno_tools import resize_image as resize_img

from PIL import Image

__all__ = ['GalenoReport', 'Patient', 'Evaluation', 'Prescription',
    'Appointment']


class GalenoReport(CompanyReport):

    @classmethod
    def get_context(cls, records, data):
        pool = Pool()
        Configuration = pool.get('galeno.configuration')
        config = Configuration(1)
        report_context = super(GalenoReport, cls).get_context(records, data)
        report_context['resize_image'] = cls.resize_image
        report_context['professional'] = cls.professional()
        report_context['action_id'] = data.get('action_id')
        report_context['signatures'] = cls.signatures
        logo = config.get_multivalue('logo')
        if logo:
            logo_image = Image.open(BytesIO(logo))
            report_context['logo_image'] = logo
            report_context['logo_size'] = tuple(x * 10 for x in logo_image.size)
        else:
            report_context['logo_image'] = None
            report_context['logo_size'] = (0, 0)
        return report_context

    @classmethod
    def resize_image(cls, data, size=(500, 500), fit=True):
        return resize_img(data, size, fit)

    @classmethod
    def professional(cls):
        if Transaction().context.get('professional'):
            Professional = Pool().get('galeno.professional')
            return Professional(Transaction().context['professional'])
        return None

    @classmethod
    def signatures(cls, action_id=None):
        signatures = []
        if action_id:
            pool = Pool()
            ActionReport = pool.get('ir.action.report')
            action_report = ActionReport(action_id)
            for signature in action_report.signatures:
                signatures.append({
                    'sign': signature.sign,
                    'position': signature.position,
                })
        return signatures


class Patient(GalenoReport):
    __name__ = 'galeno.patient'


class Evaluation(GalenoReport):
    __name__ = 'galeno.patient.evaluation'

    @classmethod
    def get_context(cls, records, data):
        report_context = super(Evaluation, cls).get_context(records, data)
        report_context['rpe'] = cls.rpe
        report_context['ms'] = cls.ms
        return report_context

    @classmethod
    def rpe(cls, record):
        result = {}
        sections = {}
        sections['rpe_oropharynx'] = ['rpe_oropharynx_lips',
            'rpe_oropharynx_tongue', 'rpe_oropharynx_pharynx',
            'rpe_oropharynx_tonsils', 'rpe_oropharynx_teeth']
        sections['rpe_nose'] = [
            'rpe_nose_partition', 'rpe_nose_turbinates', 'rpe_nose_mocous',
            'rpe_nose_paranasal_sinuses']
        sections['rpe_ear'] = ['rpe_ear_extern', 'rpe_ear_pavilion',
            'rpe_ear_eardrums']
        sections['rpe_eyes'] = ['rpe_eyes_conjunctive', 'rpe_eyes_pupils',
            'rpe_eyes_motility']
        sections['rpe_column'] = ['rpe_column_flexibility',
            'rpe_column_deviation', 'rpe_column_pain']
        sections['rpe_chest'] = ['rpe_chest_mammary_glands', 'rpe_chest_heart',
            'rpe_chest_lungs', 'rpe_chest_ribs']
        sections['rpe_limbs'] = ['rpe_limbs_vascular', 'rpe_limbs_superior',
            'rpe_limbs_inferior']
        sections['rpe_neuro'] = ['rpe_neuro_strength', 'rpe_neuro_sensivity',
            'rpe_neuro_march']
        sections['rpe_neck'] = ['rpe_neck_thyroid', 'rpe_neck_mobility']
        sections['rpe_pelvis'] = ['rpe_pelvis_pelvis', 'rpe_pelvis_genitals']
        sections['rpe_abdomen'] = ['rpe_abdomen_viscera',
            'rpe_abdomen_abdominal_wall']
        sections['rpe_skin'] = ['rpe_skin_scars', 'rpe_skin_tatoo',
            'rpe_skin_facer']
        for section, fields in sections.items():
            result[section] = {}
            for field in fields:
                if getattr(record, field):
                    result[section][field[len(section) + 1:]] = True
        return result

    @classmethod
    def ms(cls, record):
        fields = ['ms_violent_behavior',
            'ms_orientation', 'ms_perception_reality',
            'ms_abstraction', 'ms_calc_skill', 'ms_memory', 'ms_discernment',
            'ms_vocabulary', 'ms_object_recognition']
        for field in fields:
            if getattr(record, field):
                return True
        return False


class Prescription(GalenoReport):
    __name__ = 'galeno.patient.prescription'


class Appointment(GalenoReport):
    __name__ = 'galeno.patient.appointment'
