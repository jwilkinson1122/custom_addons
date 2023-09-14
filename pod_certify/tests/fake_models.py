from odoo import fields, models


class PodiatryCertify(models.Model):
    _name = "pod.certify.demo"
    _inherit = "digest.base"
    _description = "Demo digest"

    name = fields.Char(required=True)

    def _generate_serializer(self):
        result = super(PodiatryCertify, self)._generate_serializer()
        result["name"] = self.name
        return result
