import re
import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.fields import Command


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    product = fields.Char(string='Product Code',)

    @api.onchange('product_id')
    def onchange_product_id(self):
        product_id = self.env['product.product'].sudo().search([('id', '=', self.product_id.id)])
        if product_id:
            for product in product_id.product_customer_code_ids:
                if product.name_id.id == self.order_id.partner_id.id:
                    self.product = product.product_code

    def _prepare_invoice_line(self, **optional_values):
       
        self.ensure_one()
        res = {
            'display_type': self.display_type or 'product',
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [Command.set(self.tax_id.ids)],
            'analytic_distribution': self.analytic_distribution,
            'sale_line_ids': [Command.link(self.id)],
            'product_code_ids' : self.product,
            'is_downpayment': self.is_downpayment,
        }
        analytic_account_id = self.order_id.analytic_account_id.id
        if analytic_account_id and not self.display_type:
            res['analytic_distribution'] = res['analytic_distribution'] or {}
            if self.analytic_distribution:
                res['analytic_distribution'][analytic_account_id] = self.analytic_distribution.get(analytic_account_id, 0) + 100
            else:
                res['analytic_distribution'][analytic_account_id] = 100
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res

   
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    product_code_ids = fields.Char( string='Product Code')