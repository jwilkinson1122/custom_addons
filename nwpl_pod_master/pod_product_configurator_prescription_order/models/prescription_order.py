from odoo import models


class PrescriptionOrder(models.Model):
    _inherit = "prescription.order"

    def action_config_start(self):
        """Return action to start configuration wizard"""
        configurator_obj = self.env["product.configurator.prescription.order"]
        ctx = dict(
            self.env.context,
            default_order_id=self.id,
            wizard_model="product.configurator.prescription.order",
            allow_preset_selection=True,
        )
        return configurator_obj.with_context(**ctx).get_wizard_action()
