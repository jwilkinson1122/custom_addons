from odoo import models,fields,api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.picking_policy = self.partner_id.picking_policy
    
    def action_confirm(self):
        for order in self:
            if self.env.context.get('from_wizard', False):
                # Bypass the wizard check if coming from the wizard,avoid re-triggering the wizard.
                return super(SaleOrder, self).action_confirm()
            if order.partner_id.picking_policy != order.picking_policy:
                view = self.env.ref('customer_shipping_policy.view_sale_order_shipping_policy_wizard')
                context = {
                    'default_message': 'The shipping policy for this order is different from the customer\'s default shipping policy. Do you want to confirm or cancel?',
                    'default_order_id': order.id,
                    'from_wizard': True  # Add this flag to context 
                }
                return {
                    'name': 'Shipping Policy Confirmation',
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.order.shipping.policy.wizard',
                    'view_mode': 'form',
                    'view_id': view.id,
                    'target': 'new',
                    'context': context,
                }
        return super(SaleOrder, self).action_confirm()