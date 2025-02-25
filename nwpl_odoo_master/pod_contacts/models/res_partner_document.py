from odoo import fields, api, models


class PartnerDocuments(models.Model):
    _name = "res.partner.document"
    _description = "partner document"

    name = fields.Char(string="Name")
    file = fields.Binary(string="File")
    partner_id = fields.Many2one("res.partner", string="Partner", ondelete="cascade")
