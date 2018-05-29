from trytond.model import fields, Unique

__all__ = ['BasicMixin', 'CoreMixin']


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
