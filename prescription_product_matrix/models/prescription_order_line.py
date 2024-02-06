

from odoo import fields, models


class PrescriptionOrderLine(models.Model):
    _inherit = 'prescription.order.line'

    product_add_mode = fields.Selection(related='product_template_id.product_add_mode', depends=['product_template_id'])
