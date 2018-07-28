from trytond.model import ModelSQL, ModelView, fields, sequence_ordered
from trytond.pool import PoolMeta

__all__ = ['ActionReport', 'ActionReportSignature']


class ActionReport(metaclass=PoolMeta):
    __name__ = 'ir.action.report'
    signatures = fields.One2Many(
        'ir.action.report.signature', 'report', 'Signatures')


class ActionReportSignature(sequence_ordered(), ModelSQL, ModelView):
    'Report Signature'
    __name__ = 'ir.action.report.signature'

    report = fields.Many2One(
        'ir.action.report', 'Report', required=True, ondelete='CASCADE')
    sign = fields.Char('Sign', required=True)
    position = fields.Char('Position')
