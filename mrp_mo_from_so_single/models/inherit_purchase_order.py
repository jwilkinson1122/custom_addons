from odoo import api, fields, models


class InheritPurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    product_area = fields.Float(string="Area", compute='compute_area')
    area_type = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Select", default='area')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    disc = fields.Float(string='Discount (%)', digits='Discount', default=0.0, compute='recompute_discount')


    def recompute_discount(self):
        for rec in self:
            rec.disc = (rec.product_area * - 100) + 100




    @api.onchange('product_length')
    def compute_area(self):
        for rec in self:
            if rec.product_width and rec.product_length:
                if rec.area_type == 'area':
                    rec.product_area = (rec.product_width * rec.product_length) / 10000
                elif rec.area_type == 'linear':
                    rec.product_area = ((rec.product_width + rec.product_length) * 2) / 100
            else:
                rec.product_area = 1

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(**line._prepare_compute_all_values())
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'] * line.product_area,
            })




    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        aml_currency = move and move.currency_id or self.currency_id
        date = move and move.date or fields.Date.today()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': '%s: %s' % (self.order_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'discount': self.disc,
            'product_width': self.product_width,
            'product_length': self.product_length,
            'product_area': self.product_area,
            'quantity': self.qty_to_invoice,
            'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'purchase_line_id': self.id,
        }
        if not move:
            return res