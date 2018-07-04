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
    patient_ = fields.Many2One('galeno.patient', 'Patient')

    @staticmethod
    def default_period():
        return 'month'


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
        query = evaluation.select(
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
