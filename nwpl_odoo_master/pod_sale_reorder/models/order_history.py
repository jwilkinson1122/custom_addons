from odoo import fields, models, api


SALE_ORDER_STATE = [
    ("draft", "Quotation"),
    ("sent", "Quotation Sent"),
    ("sale", "Sales Order"),
    ("cancel", "Cancelled"),
]


class OrderHistory(models.Model):
    _name = "order.history"
    _description = "Order History Page"

    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    line_id = fields.Many2one(comodel_name="sale.order.line", string="Order")

    order_number = fields.Char(string="Sale Order", readonly=True)
    order_date = fields.Datetime(string="Order Date", readonly=True)
    order_product = fields.Char(string="Product", readonly=True)
    order_price = fields.Float(string="Price", readonly=True)
    order_quantity = fields.Float(string="Quantity", readonly=True)
    order_unit = fields.Char(string="Unit", default="Units", readonly=True)
    order_discount = fields.Float(string="Discount(%)", default=0.0, readonly=True)
    order_sub_total = fields.Float(
        string="Sub Total", compute="_compute_amount", store=True, readonly=True
    )
    order_status = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Order Status",
        readonly=True,
        default="draft",
    )

    @api.depends("order_quantity", "order_price")
    def _compute_amount(self):
        for record in self:
            record.order_sub_total = record.order_quantity * record.order_price

    def button_history_add_to_order(self):
        self.add_option_to_order()

    def add_option_to_order(self):
        self.ensure_one()
        values = self._get_values_to_add_to_order()
        order_line = self.env["sale.order.line"].create(values)
        self.write({"line_id": order_line.id})
        return order_line

    def _get_values_to_add_to_order(self):
        self.ensure_one()
        product = self.env["product.product"].search(
            [("name", "=", self.order_product)], limit=1
        )
        return {
            "order_id": self.sale_order_id.id,
            "price_unit": self.order_price,
            "name": self.order_product,
            "product_id": product.id,  # Pass the product ID
            "product_uom_qty": self.order_quantity,
            "discount": self.order_discount,
        }
