from odoo import api, fields, models


class SaleOrderCancel(models.TransientModel):
    _inherit = "sale.order.cancel"

    display_prescriptions_alert = fields.Boolean(
        string="Prescription Order Alert",
        compute='_compute_display_prescriptions_alert'
    )

    @api.depends('order_id')
    def _compute_display_prescriptions_alert(self):
        for wizard in self:
            wizard.display_prescriptions_alert = bool(
                wizard.order_id.prescription_count
            )
