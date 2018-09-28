from collections import defaultdict

from trytond.model import ModelView, ModelSQL, fields, DeactivableMixin
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.tools import grouped_slice, reduce_ids

__all__ = ['Professional']


class Professional(DeactivableMixin, ModelSQL, ModelView):
    'Professional'
    __name__ = 'galeno.professional'

    name = fields.Char('Name', required=True)
    prefix = fields.Char('Prefix', help="Ex: Mr., Mrs, etc")
    speciality = fields.Many2One('galeno.speciality', 'Speciality')
    position = fields.Char('Position')
    medical_identifier = fields.Char('Medical Identifier')
    galeno_groups = fields.Function(
        fields.Many2Many('galeno.group', None, None, 'Groups'),
        'get_groups', searcher='search_galeno_groups')

    def get_rec_name(self, name):
        return "%s %s" % (self.prefix, self.name)

    @classmethod
    def get_groups(cls, professionals, name):
        pool = Pool()
        cursor = Transaction().connection.cursor()
        result = defaultdict(lambda: [])
        GalenoGroupUserRel = pool.get('galeno.group-related-res.user')
        galeno_group_user_rel = GalenoGroupUserRel.__table__()
        User = pool.get('res.user')
        user = User.__table__()
        ids = [p.id for p in professionals]
        for sub_ids in grouped_slice(ids):
            red_sql = reduce_ids(user.professional, sub_ids)
            query = galeno_group_user_rel.join(user,
                condition=galeno_group_user_rel.user == user.id
            ).select(
                user.professional,
                galeno_group_user_rel.group,
                where=red_sql
            )
            cursor.execute(*query)
            for prof_id, group_id in cursor.fetchall():
                result[prof_id].append(group_id)
        return result

    @classmethod
    def search_galeno_groups(cls, name, clause):
        pool = Pool()
        _, operator, value = clause
        Operator = fields.SQL_OPERATORS[operator]
        GalenoGroupUserRel = pool.get('galeno.group-related-res.user')
        galeno_group_user_rel = GalenoGroupUserRel.__table__()
        User = pool.get('res.user')
        user = User.__table__()
        query = galeno_group_user_rel.join(user,
            condition=galeno_group_user_rel.user == user.id
        ).select(
            user.professional,
            where=Operator(galeno_group_user_rel.group, value)
        )
        return [('id', 'in', query)]
