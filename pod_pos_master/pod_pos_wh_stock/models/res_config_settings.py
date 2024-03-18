


from odoo import models, fields


class posConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_pod_display_stock = fields.Boolean(
        related="pos_config_id.pod_display_stock", readonly=False)
    pos_pod_display_by = fields.Selection(
        related="pos_config_id.pod_display_by", readonly=False)
    pos_pod_min_qty = fields.Integer(
        related="pos_config_id.pod_min_qty", readonly=False)
    pos_pod_show_qty_location = fields.Boolean(
        related="pos_config_id.pod_show_qty_location", readonly=False)
    pos_pod_pos_location = fields.Many2one(
        related="pos_config_id.pod_pos_location", readonly=False)
