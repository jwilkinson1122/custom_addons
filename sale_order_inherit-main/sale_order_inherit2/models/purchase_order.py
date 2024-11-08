from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_booking = fields.Boolean(string='Is Booking', default=False)
    booking_order_id = fields.Many2one('sale.order', string='Booking Order')

    def write(self, vals):
        for record in self:
            if record.is_booking:
                vals['name'] = self.env['ir.sequence'].next_by_code('request.quotation') or _('New')
        return super(PurchaseOrder, self).write(vals)

    # point 10
    def action_view_booking_orders(self):
        if self.is_booking:
            action = self.env.ref('sale.action_quotations').read()[0]
            action['domain'] = [('id', '=', self.booking_order_id.id)]
            return action
        else:
            return {
                'warning': {
                    'title': 'Not a Booking Order',
                    'message': 'This record is not a booking order.',
                }
            }
