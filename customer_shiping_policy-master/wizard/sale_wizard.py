from odoo import models, fields, api

class SaleOrderShippingPolicyWizard(models.TransientModel):
    _name = 'sale.order.shipping.policy.wizard'
    _description = 'Sale Order Shipping Policy Confirmation'

    message = fields.Text(string='Message', readonly=True)
    order_id = fields.Many2one('sale.order', string='Order', required=True)


    @api.model
    def default_get(self, fields):
        res = super(SaleOrderShippingPolicyWizard, self).default_get(fields)
        if 'default_message' in self.env.context:
            res['message'] = self.env.context['default_message']
        if 'default_order_id' in self.env.context:
            res['order_id'] = self.env.context['default_order_id']
        return res

    
    def confirm(self):
        sale_order = self.env['sale.order'].browse(self.order_id.id)
        sale_order.action_confirm()
        return {'type': 'ir.actions.act_window_close'}
    
    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
