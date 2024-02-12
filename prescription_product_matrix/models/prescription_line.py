

from odoo import fields, models


class PrescriptionLine(models.Model):
    _inherit = 'prescription.line'

    product_add_mode = fields.Selection(related='product_template_id.product_add_mode', depends=['product_template_id'])
