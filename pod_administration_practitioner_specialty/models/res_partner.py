

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    specialty_ids = fields.Many2many("pod.specialty", string="Specialties")
