from odoo import models, fields

class Productinherit(models.Model):
    _inherit = 'product.template'

    pod_order_label_demo_product = fields.Boolean(string="Orderline Label")
