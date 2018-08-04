from sql import Literal, Window
from sql.aggregate import Count
from sql.functions import RowNumber, CurrentTimestamp


from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = ['ReportEvaluationContext', 'ReportEvaluation']


class QueryContext(object):
    "Generic Query Context Model"

    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    professional_ = fields.Many2One('galeno.professional', 'Professional')
    speciality_ = fields.Many2One('galeno.speciality', 'Speciality')
    patient_ = fields.Many2One('galeno.patient', 'Patient')
    gender_ = fields.Selection([
        (None, ''),
        ('male', 'Male'),
        ('female', 'Female')
    ], 'Gender')


class ReportEvaluationContext(QueryContext, ModelView):
    "Evaluation Context Model"
    __name__ = 'galeno.report.evaluation.context'


class ReportEvaluation(ModelSQL, ModelView):
    "Evaluation Reporting"
    __name__ = 'galeno.report.evaluation'

    number = fields.Integer('Number')
    state = fields.Selection([
        ('all', 'All'),
        ('initial', 'initiated'),
        ('finish', 'finished'),
        ('cancel', 'canceled'),
    ], 'State', sort=False)
    state_string = state.translated('state')

    @classmethod
    def __setup__(cls):
        super(ReportEvaluation, cls).__setup__()
        cls._order.insert(0, ('state', 'ASC'))

    @classmethod
    def query_get(cls, state='all'):
        pool = Pool()
        Evaluation = pool.get('galeno.patient.evaluation')
        evaluation = Evaluation.__table__()
        Patient = pool.get('galeno.patient')
        patient = Patient.__table__()
        Professional = pool.get('galeno.professional')
        professional = Professional.__table__()

        context = Transaction().context
        where = Literal(True)
        columns = [
            evaluation.state,
        ]
        if context.get('start_date'):
            where &= (evaluation.start_date >= context.get('start_date'))
        if context.get('end_date'):
            where &= (evaluation.end_date <= context.get('end_date'))
        if context.get('patient_'):
            where &= (evaluation.patient == context.get('patient_'))
        if context.get('professional_'):
            where &= (evaluation.professional == context.get('professional_'))
        if context.get('gender_'):
            where &= (patient.gender == context.get('gender_'))
        if context.get('speciality_'):
            where &= (professional.speciality == context.get('speciality_'))

        query = evaluation.join(patient,
            condition=patient.id == evaluation.patient
        ).join(professional,
            condition=professional.id == evaluation.professional
        ).select(
            *columns + [
                Literal(0).as_('create_uid'),
                CurrentTimestamp().as_('create_date'),
                Literal(0).as_('write_uid'),
                CurrentTimestamp().as_('write_date'),
                RowNumber(window=Window([])).as_('id'),
                Count(evaluation.id).as_('number'),
            ],
            where=where,
            group_by=columns
        )
        return query

    @classmethod
    def table_query(cls):
        return cls.query_get()
