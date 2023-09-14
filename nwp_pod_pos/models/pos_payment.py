

from odoo import fields, models


class PosPayment(models.Model):
    _inherit = "pos.payment"

    encounter_id = fields.Many2one("pod.encounter")
