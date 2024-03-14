

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pod_remove_all_item = fields.Boolean(string="Remove All Item From Cart")
    pod_validation_to_remove_all_item  = fields.Boolean(string="Ask for confirmation to remove all item")
    pod_validation_to_remove_single_item = fields.Boolean(string="Ask for confirmation to remove single item")
    