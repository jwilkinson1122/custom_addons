from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    integer_practice_identifier = fields.Integer()
    authorization_web_id = fields.Many2one("pod.authorization.web")
    authorization_information = fields.Text()
