from odoo import fields, models


class PodCertify(models.Model):
    _name = "pod.certify.demo"
    _inherit = "digest.base"

    name = fields.Char(required=True)

    def _generate_serializer(self):
        result = super(PodCertify, self)._generate_serializer()
        result["name"] = self.name
        return result
