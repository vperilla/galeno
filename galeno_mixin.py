from trytond.model import fields, Unique

__all__ = ['BasicMixin']


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
