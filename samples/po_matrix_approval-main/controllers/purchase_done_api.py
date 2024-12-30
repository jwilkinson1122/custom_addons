from odoo import http
from odoo.http import request

class PurchaseOrderController(http.Controller):

    @http.route('/confirm-purchase-orders', type='http', auth="user")
    def confirm_purchase_orders(self, **kw):
        purchase_orders = request.env['purchase.order'].sudo().search([('state', '=', 'draft')])

        for order in purchase_orders:
            order.button_confirm()

        return "Purchase orders confirmed successfully. Well done!"

    @http.route('/confirm-purchase-order/<int:order_id>', type='http', auth="user")
    def confirm_purchase_order_by_id(self, order_id, **kw):
        purchase_order = request.env['purchase.order'].sudo().browse(order_id)
        if purchase_order and purchase_order.state == 'draft':
            purchase_order.button_confirm()
            return f"Purchase order with ID {order_id} confirmed successfully. Well done!"
        else:
            return f"Purchase order with ID {order_id} not found or not in draft state."