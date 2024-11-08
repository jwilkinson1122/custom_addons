from odoo import fields, models, tools, api, _


class RoomBookingLine(models.Model):
    """Model that handles the room booking form"""

    _name = "room.booking.line"
    _description = "Prescription Summary Line"

    @tools.ormcache()
    def _set_default_uom_id(self):
        return self.env.ref("uom.product_uom_day")

    booking_id = fields.Many2one(
        "room.booking", string="Booking", help="Indicates the Room", ondelete="cascade"
    )
    checkin_date = fields.Datetime(
        string="Check In",
        help="You can choose the date," " Otherwise sets to current Date",
        required=True,
    )
    checkout_date = fields.Datetime(
        string="Check Out",
        help="You can choose the date," " Otherwise sets to current Date",
        required=True,
    )
    room_id = fields.Many2one(
        "prescription.room",
        string="Room",
        domain=[("status", "=", "available")],
        help="Indicates the Room",
        required=True,
    )
    uom_qty = fields.Float(
        string="Duration",
        help="The quantity converted into the UoM used by " "the product",
        readonly=True,
    )
    uom_id = fields.Many2one(
        "uom.uom",
        default=_set_default_uom_id,
        string="Unit of Measure",
        help="This will set the unit of measure used",
        readonly=True,
    )
    price_unit = fields.Float(
        related="room_id.list_price",
        string="Rent",
        digits="Product Price",
        help="The rent price of the selected room.",
    )
    tax_ids = fields.Many2many(
        "account.tax",
        "prescription_room_order_line_taxes_rel",
        "room_id",
        "tax_id",
        string="Taxes",
        help="Default taxes used when selling the room.",
        domain=[("type_tax_use", "=", "sale")],
    )
    # related
    currency_id = fields.Many2one(
        string="Currency",
        related="booking_id.pricelist_id.currency_id",
        help="The currency used",
    )
    price_subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_price_subtotal",
        help="Total Price excluding Tax",
        store=True,
    )
    price_tax = fields.Float(
        string="Total Tax",
        compute="_compute_price_subtotal",
        help="Tax Amount",
        store=True,
    )
    price_total = fields.Float(
        string="Total",
        compute="_compute_price_subtotal",
        help="Total Price including Tax",
        store=True,
    )
    state = fields.Selection(
        related="booking_id.state",
        string="Order Status",
        help=" Status of the Order",
        copy=False,
    )
    booking_line_visible = fields.Boolean(
        default=False,
        string="Booking Line Visible",
        help="If True, then Booking Line " "will be visible",
    )

    def _compute_price_subtotal(self):
        pass
