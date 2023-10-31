from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_device_configurator(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "product_device_configurator.device_configure_action"
        )
        action['context'] = {
            'active_model': self._name,
            'active_ids': self.ids,
            'active_id': self.id,
        }
        return action
