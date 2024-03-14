from odoo import api, fields, models, _


class InheritSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_dimension = fields.Char(string="Dimensions")
    product_width = fields.Float(string="Width")
    product_height = fields.Float(string="Height")
    product_area = fields.Float(string="Area", compute='compute_area')
    # index_num = fields.Integer(string="Index No")
    quantity_appear = fields.Float(string="Qty", default=1.0)
    area_compute = fields.Selection([('area', 'Area'), ('linear', 'Linear')], string="Area Select")
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0,
                                   compute='compute_quantity')

    @api.onchange('area_compute')
    def compute_area(self):
        for rec in self:
            if rec.product_width and rec.product_height:
                if rec.area_compute == 'area':
                    rec.product_area = (rec.product_width * rec.product_height) / 10000
                elif rec.area_compute == 'linear':
                    rec.product_area = ((rec.product_width + rec.product_height) * 2) / 10000
                rec.product_uom_qty = rec.product_area
            else:
                rec.product_area = 1
                rec.product_uom_qty = rec.product_area

    @api.onchange('quantity_appear')
    def compute_quantity(self):
        for rec in self:
            rec.product_uom_qty = rec.quantity_appear * rec.product_area

    source_order = fields.Char(string="SO Name", related="order_id.name")
    partner_name = fields.Char(string="Customer", related="order_id.partner_id.name")
    total_order_amount = fields.Monetary(string="SO Total", related="order_id.amount_total")
    person_sale = fields.Char(string="Sales Person", related="order_id.user_id.name")
    order_date = fields.Datetime(string="Order Date", related="order_id.date_order")
    product_name = fields.Char(string="Product Name", related="product_template_id.name")
    status_invoice = fields.Selection(string="Invoice Status", related="order_id.invoice_status")


class SaleOrderInheritance(models.Model):
    _inherit = 'sale.order'

    total_areas = fields.Float(string="Total Area", compute='compute_total_areas')

    @api.depends('order_line')
    def compute_total_areas(self):
        for rec in self:
            list_areas = []
            for lines in rec.order_line:
                if lines.product_width > 0 and lines.product_height > 0:
                    sum_totals = lines.product_area
                    list_areas.append(sum_totals)

            rec.total_areas = sum(list_areas)
