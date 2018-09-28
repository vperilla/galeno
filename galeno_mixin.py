from trytond.model import ModelView, fields, Unique
from trytond.pyson import Bool, Eval, If, Id
from trytond.transaction import Transaction

__all__ = ['BasicMixin', 'CoreMixin', 'GalenoContext', 'GalenoShared']


class BasicMixin(object):

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True, translate=True)

    @classmethod
    def __setup__(cls):
        super(BasicMixin, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_uniq', Unique(t, t.name), 'Name must be unique !'),
            ('code_uniq', Unique(t, t.code), 'CODE must be unique !'),
        ]
        cls._order.insert(0, ('name', 'ASC'))


class CoreMixin(object):

    core = fields.Boolean('Core')

    @classmethod
    def __setup__(cls):
        super(CoreMixin, cls).__setup__()
        cls._error_messages.update({
            'unmodified': ('Can not modified "%(record)s" '
                'because is part  of core.'),
            })

    @staticmethod
    def default_core():
        return False

    @classmethod
    def delete(cls, records):
        for record in records:
            if record.core == True:
                cls.raise_user_error('unmodified', {
                    'record': record.rec_name,
                })
        super(CoreMixin, cls).delete(records)

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        for records, values in zip(actions, actions):
            for record in records:
                if record.core == True:
                    cls.raise_user_error('unmodified', {
                        'record': record.rec_name,
                    })
        super(CoreMixin, cls).write(*args)


class GalenoContext(ModelView):
    'Galeno Context'
    __name__ = 'galeno.context'

    galeno_group_filter = fields.Many2One('galeno.group', 'Group',
        domain=[
            ('id', 'in', Eval('context', {}).get('galeno_groups', [])),
        ], depends=['state'], required=True)
    professional_filter = fields.Many2One('galeno.professional', 'Professional',
        states={
            'required': ~Id('galeno',
                'group_galeno_share').in_(
                Eval('context', {}).get('groups', [])),
        },
        domain=[If(Id('galeno',
                'group_galeno_share').in_(
                Eval('context', {}).get('groups', [])),
            [('galeno_groups', 'in', [Eval('galeno_group_filter')])],
            [('id', If(Bool(
                Eval('context', {}).get('professional', False)), '=', '!='),
                Eval('context', {}).get('professional', -1)),
            ('galeno_groups', 'in', [Eval('galeno_group_filter')])]),
        ], depends=['galeno_group_filter'])

    @staticmethod
    def default_professional_filter():
        if Transaction().context.get('professional'):
            return Transaction().context['professional']

    @classmethod
    def default_galeno_group_filter(cls):
        context = Transaction().context
        if context.get('galeno_groups'):
            return context['galeno_groups'][0]


class GalenoShared(object):
    'Galeno Shared Object'

    company = fields.Many2One('company.company', 'Company', required=True,
        states={
            'invisible': True,
        })
    galeno_group = fields.Many2One('galeno.group', 'Group',
        states={
            'readonly': ~Eval('state').in_(['scheduled']),
        },
        domain=[
            ('id', 'in', Eval('context', {}).get('galeno_groups', [])),
        ], depends=['state'], required=True, select=True)
    professional = fields.Many2One('galeno.professional', 'Professional',
        states={
            'readonly': ~Eval('state').in_(['scheduled']),
        },
        domain=[
            ('id', If(Bool(
                Eval('context', {}).get('professional', False)), '=', '!='),
                Eval('context', {}).get('professional', -1)),
            ('galeno_groups', 'in', [Eval('galeno_group')]),
        ], depends=['state', 'galeno_group'], required=True, select=True)

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_professional():
        return Transaction().context.get('professional')

    @classmethod
    def default_galeno_group(cls):
        context = Transaction().context
        if context.get('galeno_groups'):
            if context.get('galeno_group_filter'):
                return context['galeno_group_filter']
            return context['galeno_groups'][0]

    @fields.depends('galeno_group', 'professional')
    def on_change_galeno_group(self, name=None):
        if Transaction().context.get('professional') is None:
            self.professional = None

    @classmethod
    def search(cls, args, offset=0, limit=None, order=None, count=False,
            query=False):
        args = args[:]
        context = Transaction().context
        if context.get('galeno_group_filter'):
            args = ['AND',
                ('galeno_group', '=', context['galeno_group_filter']), args[:]]
        if context.get('professional_filter'):
            args = ['AND',
                ('professional', '=', context['professional_filter']), args[:]]
        return super(GalenoShared, cls).search(args, offset=offset,
            limit=limit, order=order, count=count, query=query)
