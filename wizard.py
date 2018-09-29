from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import (Wizard, StateAction, StateView, StateTransition,
    Button)

__all__ = ['EvolutionGraphStart', 'EvolutionGraph']


class EvolutionGraphStart(ModelView):
    'Open Evolution Graph Start'
    __name__ = 'galeno.evolution.graph.start'

    patient = fields.Many2One('galeno.patient', 'Patient', required=True)
    type_ = fields.Selection(
        [
            ('weight', 'Weight'),
            ('heigth', 'Heigth'),
        ], 'Type', sort=False, required=True)


class EvolutionGraph(Wizard):
    'Open Evolution Graph'
    __name__ = 'galeno.evolution.graph'

    start = StateView('galeno.evolution.graph.start',
        'galeno.evolution_graph_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'handle', 'tryton-ok', default=True),
            ])
    handle = StateTransition()
    open_weight = StateAction('galeno.act_evolution_weight')
    open_heigth = StateAction('galeno.act_evolution_heigth')

    def default_start(self, fields):
        pool = Pool()
        context = Transaction().context
        active_model = context.get('active_model')
        if active_model == 'galeno.patient':
            return {
                'patient': context.get('active_id'),
            }
        elif active_model == 'galeno.patient.evaluation':
            Evaluation = pool.get('galeno.patient.evaluation')
            evaluation = Evaluation(context.get('active_id'))
            return {
                'patient': evaluation.patient.id,
            }

    def transition_handle(self):
        return 'open_%s' % (self.start.type_)

    def get_evaluations(self):
        pool = Pool()
        Evaluation = pool.get('galeno.patient.evaluation')
        evaluations = Evaluation.search([
            ('patient', '=', self.start.patient),
            ('state', '=', 'finish'),
        ])
        return [e.id for e in evaluations]

    def do_open_weight(self, action):
        data = {'res_id': self.get_evaluations()}
        return action, data

    def do_open_heigth(self, action):
        data = {'res_id': self.get_evaluations()}
        return action, data
