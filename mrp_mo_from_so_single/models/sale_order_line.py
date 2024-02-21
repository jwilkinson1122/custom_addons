from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DescDetailsLine(models.Model):
    _name = "desc.detail"
    _description = "desc.detail"

    name = fields.Char()


class InheritSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    index_number = fields.Char(string="Index No", compute="compute_index")
    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    product_area = fields.Float(string="Area", compute='compute_area')
    date = fields.Date(string="Date")
    area_type = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Select", default='area')
    desc_ids = fields.Many2many('desc.detail')
    price_subtotal = fields.Monetary(compute='compute_amount', string='Subtotal', store=True)
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

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'] * line.product_area,
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    def compute_index(self):
        for rec in self:
            rec.index_number = rec.sequence - 9

    def create_mo_from_boms(self):
        for rec in self:
            product_template = rec.product_id.product_tmpl_id
            boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_template.id)])
            company_id = self.env.company
            moves_list = []
            src_locations = \
                self.env['stock.location'].search([('company_id', '=', company_id.id), ('usage', '=', 'internal')])[0]
            dest_locations = \
                self.env['stock.location'].search([('company_id', '=', company_id.id), ('name', '=', 'Production')])[0]
            if boms:
                bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_template.id)])
                for line in bom.bom_line_ids:
                    val = {
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_uom_qty': line.product_qty,
                        'product_uom': line.product_id.uom_id.id,
                        'location_id': src_locations.id,
                        'location_dest_id': dest_locations.id,
                    }
                    moves = self.env['stock.move'].create(val)
                    moves_list.append(moves.id)
            else:
                # bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_template.id)])
                # for line in bom.bom_line_ids:
                # cutting_product = self.env['product.product'].browse(2)
                cuting_product = self.env['product.product'].search([('name', '=', 'cuting_product')])
                if not cuting_product:
                    cuting_product = self.env['product.product'].create({
                        'name': 'cuting_product',
                        'detailed_type': 'consu',

                    })
                val = {
                    'product_id': cuting_product.id,
                    'name': cuting_product.name,
                    'product_uom_qty': 1,
                    'product_uom': cuting_product.uom_id.id,
                    'location_id': src_locations.id,
                    'location_dest_id': dest_locations.id,
                }
                moves = self.env['stock.move'].create(val)
                moves_list.append(moves.id)

            vals = {
                'product_id': rec.product_id.id,
                'product_qty': rec.product_uom_qty,
                'product_uom_id': rec.product_id.uom_id.id,
                'product_width': rec.product_width,
                'product_length': rec.product_length,
                'product_area': rec.product_area,
                'order_index': rec.index_number,
                'sale_order_id': rec.order_id.id,
                'move_raw_ids': moves_list,
            }
            mo = self.env['mrp.production'].create(vals)
            rec.order_id.related_mo_ids += mo

    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_width': self.product_width,
            'product_length': self.product_length,
            'product_area': self.product_area,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.disc,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if self.order_id.analytic_account_id and not self.display_type:
            res['analytic_account_id'] = self.order_id.analytic_account_id.id
        if self.analytic_tag_ids and not self.display_type:
            res['analytic_tag_ids'] = [(6, 0, self.analytic_tag_ids.ids)]
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res
