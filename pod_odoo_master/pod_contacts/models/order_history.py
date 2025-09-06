from odoo import fields, models, api, _
from odoo.exceptions import UserError

SALE_ORDER_STATE = [
    ("draft", "Quotation"),
    ("sent", "Quotation Sent"),
    ("sale", "Sales Order"),
    ("cancel", "Cancelled"),
]

# INVOICE_STATUS = [
#     ('upselling', 'Upselling Opportunity'),
#     ('invoiced', 'Fully Invoiced'),
#     ('to invoice', 'To Invoice'),
#     ('no', 'Nothing to Invoice')
# ]

# SALE_ORDER_STATE = [
#     ('draft', "Quotation"),
#     ('sent', "Quotation Sent"),
#     ('sale', "Sales Order"),
#     ('cancel', "Cancelled"),
# ]


class OrderHistory(models.Model):
    _name = "order.history"
    _description = "Order History Page"

    # sale_order_id = fields.Many2one("sale.order", string="Sale Order", required=True)
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", ondelete="cascade", required=True)
    line_id = fields.Many2one(comodel_name="sale.order.line", string="Order Line")
    product_id = fields.Many2one("product.product", string="Product", readonly=True)

    order_number = fields.Char(string="Sale Order", readonly=True)
    order_date = fields.Datetime(string="Order Date", readonly=True)
    order_product = fields.Char(string="Product", readonly=True)
    order_price = fields.Float(string="Price", readonly=True)
    order_quantity = fields.Float(string="Quantity", readonly=True)
    order_unit = fields.Char(string="Unit", default="Units", readonly=True)
    order_discount = fields.Float(string="Discount(%)", default=0.0, readonly=True)

    order_sub_total = fields.Float(
        string="Subtotal", compute="_compute_amount", store=True
    )

    order_status = fields.Selection(
        SALE_ORDER_STATE, string="Order Status", readonly=True
    )

    @api.depends("order_quantity", "order_price")
    def _compute_amount(self):
        for record in self:
            record.order_sub_total = record.order_quantity * record.order_price

    def button_history_add_to_order(self):
        self.add_option_to_order()

    def add_option_to_order(self):
        """Add product from history to the current order."""
        self.ensure_one()
        if not self.sale_order_id:
            raise ValueError(_("No Sale Order is linked to this history."))

        product = self.env["product.product"].browse(self.product_id.id)
        if not product:
            raise ValueError(_("Product not found in the system."))

        values = {
            "order_id": self.sale_order_id.id,
            "product_id": product.id,
            "name": product.name,
            "product_uom_qty": self.order_quantity,
            "price_unit": self.order_price,
            "discount": self.order_discount,
        }
        return self.env["sale.order.line"].create(values)

    def _get_values_to_add_to_order(self):
        self.ensure_one()
        product = self.env["product.product"].search(
            [("name", "=", self.order_product)], limit=1
        )
        return {
            "order_id": self.sale_order_id.id,
            "price_unit": self.order_price,
            "name": self.order_product,
            "product_id": product.id,  
            "product_uom_qty": self.order_quantity,
            "discount": self.order_discount,
        }

    # Prevent manual deletion of history that belongs to active orders
    # allow only for cancelled quotes:

    def unlink(self):
        for rec in self:
            if rec.sale_order_id and rec.sale_order_id.state != "cancel":
                raise UserError(_("You can delete history only for cancelled quotations."))
        return super().unlink()