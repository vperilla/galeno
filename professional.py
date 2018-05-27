from trytond.model import ModelView, ModelSQL, fields, DeactivableMixin

__all__ = ['Professional']


class Professional(DeactivableMixin, ModelSQL, ModelView):
    'Professional'
    __name__ = 'galeno.professional'

    name = fields.Char('Name', required=True)
    prefix = fields.Char('Prefix', help="Ex: Mr., Mrs, etc")
    speciality = fields.Many2One('galeno.speciality', 'Speciality')
    medical_identifier = fields.Char('Medical Identifier')

    def get_rec_name(self, name):
        return "%s %s" % (self.prefix, self.name)
