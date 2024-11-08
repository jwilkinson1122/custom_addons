# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class RoomBooking(models.Model):
    _name = "room.booking"
    _description = "Prescription Room Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Summary Number",
        readonly=True,
        index=True,
        default="New",
        help="Name Of Summary",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        help="chose The Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        help="Customers of Prescription",
        required=True,
        index=True,
        tracking=1,
    )  # domain (nanti diisiny)
    date_order = fields.Datetime(
        string="Order Date",
        required=True,
        copy=False,
        help="Creation date of draft/sent orders,"
        " Confirmation date of confirmed orders",
        default=fields.Datetime.now,
    )
    is_checkin = fields.Boolean(
        default=False, string="Is Checkin", help="sets to True if the room is occupied"
    )
    maintenance_request_sent = fields.Boolean(
        default=False,
        string="Maintenance Request" "or not",
        help="sets to True if the maintenance request send",
    )
    checkin_date = fields.Datetime(
        string="Check In", help="Date Of CheckIn", default=fields.Datetime.now()
    )
    checkout_date = fields.Datetime(
        string="Check Out",
        help="Date of Checkout",
        default=fields.Datetime.now() + timedelta(hours=23, minutes=59, seconds=59),
    )
    prescription_policy = fields.Selection(
        [
            ("prepaid", "On Booking"),
            ("manual", "On CheckIn"),
            ("picking", "On CheckOut"),
        ],
        default="manual",
        string="Prescription Policy",
        tracking=True,
    )
    duration = fields.Integer(
        string="Duration in Days",
        help="Number of days which will automatically "
        "count from the check-in and check-out "
        "date.",
    )
    invoice_button_visible = fields.Boolean(
        string="Invoice Button Display",
        help="Invoice button will be " "visible if this button is " "True",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("reserved", "Reserved"),
            ("checkin", "CheckIn"),
            ("checkin", "CheckIn"),
            ("checkout", "CheckOut"),
            ("cancel", "Cancel"),
            ("done", "Done"),
        ],
        string="state",
        help="State of the Booking",
        default="draft",
        tracking=True,
    )
    invoice_count = fields.Integer(
        compute="_compute_invoice_count",
        string="Invoice count",
        help="The Number of Invoice created",
    )
    invoice_status = fields.Selection(
        selection=[
            ("no_invoice", "Nothing To Invoice"),
            ("to_invoice", "To Invoice"),
            ("invoiced", "Invoiced"),
        ],
        string="Invoice Status",
        help="Status Of The Invoice",
        default="no_invoice",
        tracking=True,
    )
    prescription_invoice_id = fields.Many2one(
        "account.move", string="Invoice", help="Indicates The Invoice", copy=False
    )
    duration_visible = fields.Float(
        string="Duration", help="A Dummy field for Duration"
    )
    need_service = fields.Boolean(
        default=False,
        string="Need Service",
        help="Check if a Service to be added with the booking",
    )
    need_orthotic = fields.Boolean(
        default=False,
        string="Need Vehicle",
        help="Check if a orthotic to be added with the Booking",
    )
    need_orthotic = fields.Boolean(
        default=False,
        string="Need Orthotic",
        help="Check If A Event to be added with the booking",
    )
    need_event = fields.Boolean(
        default=False,
        string="Need Event",
        help="Check if a Event to be added with" " the Booking",
    )
    # service_line_ids = fields.One2many("service.booking.line", "booking_id", string="Service",
    #                                    help="Prescription services details provided to" "Customer and it will included in" "the main Invoices.")
    # event_line_ids = fields.One2many('event.booking.line', 'booking_id', string="Event", help="Prescription Event "
    #                                                                                           "reservation detail.")
    # orthotic_line_ids = fields.One2many('orthotic.booking.line', 'booking_id', string='Prescription room reservation detail.')
    room_line_ids = fields.One2many(
        "room.booking.line",
        "booking_id",
        string="Room",
        help="Prescription Room Reservation " "detail.",
    )
    # orthotic_order_line_ids = fields.One2many('orthotic.booking.line', 'booking_id', string='Orthotic',
    #                                       help="Orthotic details provided"
    #                                            " to Customer and"
    #                                            " it will included in the "
    #                                            "main invoice.", )
    user_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invoice",
        compute="_compute_user_id",
        help="sets the User Automatically",
        required=True,
        domain="['|', ('company_id', '=', False), "
        "('company_id', '=',"
        " company_id)]",
    )
    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Pricelist",
        compute="_compute_pricelist_id",
        store=True,
        readonly=False,
        required=True,
        tracking=1,
        help="If you change the pricelist,"
        " only newly added lines"
        " will be affected.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        help="This is the currency used",
        related="pricelist_id.currency_id",
        depends=["pricelist_id.currency_id"],
    )
    account_move = fields.Integer(
        string="Invoice Id", help="Id of the invoices created"
    )
    amount_tax = fields.Monetary(
        string="Taxes",
        help="Total Tax Amount",
        store=True,
        compute="_compute_amount_untaxed",
        tracking=4,
    )
    amount_untaxed = fields.Monetary(
        string="Total Untaxed Amount",
        help="This indicates the total untaxed" "amount",
        store=True,
    )
    amount_total = fields.Monetary(
        string="Total",
        store=True,
        help="The total Amount including Tax",
        compute="_compute_amount_untaxed",
        tracking=4,
    )
    amount_untaxed_service = fields.Monetary(
        string="Service Untaxed",
        help="Untaxed Amount for Service",
        compute="_compute_amount_untaxed",
        tracking=5,
    )
    amount_untaxed_orthotic = fields.Monetary(
        string="Amount Untaxed",
        help="Untaxed amount for Orthotic",
        compute="_compute_amount_untaxed",
        tracking=5,
    )
    amount_taxed_room = fields.Monetary(
        string="Rom Tax",
        help="Tax for Room",
        compute="_compute_amount_untaxed",
        tracking=5,
    )
    amount_untaxed_room = fields.Monetary(
        string="Room Untaxed",
        help="Untaxed Amount for Room",
        compute="_compute_amount_untaxed",
        tracking=5,
    )
    amount_untaxed_orthotic = fields.Monetary(
        string="Orthotic Untaxed",
        help="Untaxed Amount for Orthotic",
        compute="_compute_amount_untaxed",
        tracking=5,
    )
    amount_untaxed_event = fields.Monetary(
        string="Event Untaxed",
        help="Untaxed Amount for Event",
        compute="_compute_amount_untaxed",
        tracking=5,
    )
    amount_taxed_orthotic = fields.Monetary(
        string="Orthotic Tax",
        help="Tax for Orthotic",
        compute="_compute_amount_untaxed",
        tracking=5,
    )
    amount_taxed_event = fields.Monetary(
        string="Event Tax",
        help="Tax for Event",
        compute="_compute_amount_untaxed",
        tracking=5,
    )
    amount_taxed_service = fields.Monetary(
        string="Service Tax",
        compute="_compute_amount_untaxed",
        help="Tax for Service",
        tracking=5,
    )
    amount_taxed_orthotic = fields.Monetary(
        string="Orthotic Tax",
        compute="_compute_amount_untaxed",
        help="Tax for Orthotic",
        tracking=5,
    )
    amount_total_room = fields.Monetary(
        string="Total Amount for Room",
        compute="_compute_amount_untaxed",
        help="This is the Total Amount for " "Room",
        tracking=5,
    )
    amount_total_orthotic = fields.Monetary(
        string="Total Amount for Orthotic",
        compute="_compute_amount_untaxed",
        help="This is the Total Amount for " "Orthotic",
        tracking=5,
    )
    amount_total_event = fields.Monetary(
        string="Total Amount for Event",
        compute="_compute_amount_untaxed",
        help="This is the Total Amount for " "Event",
        tracking=5,
    )
    amount_total_service = fields.Monetary(
        string="Total Amount for Service",
        compute="_compute_amount_untaxed",
        help="This is the Total Amount for " "Service",
        tracking=5,
    )
    amount_total_orthotic = fields.Monetary(
        string="Total Amount for Orthotic",
        compute="_compute_amount_untaxed",
        help="This is the Total Amount for " "Orthotic",
        tracking=5,
    )

    # sequence
    @api.model
    def create(self, vals_list):
        """sequence Generation"""
        if vals_list.get("name", "New") == "New":
            vals_list["name"] = self.env["ir.sequence"].next_by_code("room.booking")
        return super().create(vals_list)

    @api.depends("partner_id")
    def _compute_user_id(self):
        """Compute the user id"""
        for order in self:
            order.user_id = (
                order.partner_id.address_get(["invoice"])["invoice"]
                if order.partner_id
                else False
            )

    def action_view_invoices(self):
        pass

    #     action reserve
    def action_reserve(self):
        pass

    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env["account.move"].search_count(
                [("ref", "=", self.name)]
            )

    def action_cancel(self):
        if self.room_line_ids:
            for room in self.room_line_ids:
                room.room_id.write(
                    {
                        "status": "available",
                    }
                )

    def _compute_amount_untaxed(self, flag=False):
        """Compute the total amounts of the Sale Order"""
        amount_untaxed_room = 0.0
        amount_untaxed_orthotic = 0.0
        amount_untaxed_orthotic = 0.0
        amount_untaxed_event = 0.0
        amount_untaxed_service = 0.0
        amount_taxed_room = 0.0
        amount_taxed_orthotic = 0.0
        amount_taxed_orthotic = 0.0
        amount_taxed_event = 0.0
        amount_taxed_service = 0.0
        amount_total_room = 0.0
        amount_total_orthotic = 0.0
        amount_total_orthotic = 0.0
        amount_total_event = 0.0
        amount_total_service = 0.0
        room_lines = self.room_line_ids
        orthotic_lines = self.orthotic_order_line_ids
        service_lines = self.service_line_ids
        orthotic_lines = self.orthotic_line_ids
        event_lines = self.event_line_ids
        booking_list = []
        account_move_line = self.env["account.move.line"].search_read(
            domain=[("ref", "=", self.name), ("display_type", "!=", "payment_term")],
            fields=["name", "quantity", "price_unit", "product_type"],
        )
        for rec in account_move_line:
            del rec["id"]
        if room_lines:
            amount_untaxed_room += sum(room_lines.mapped("price_subtotal"))
            amount_taxed_room += sum(room_lines.mapped("price_tax"))
            amount_total_room += sum(room_lines.mapped("price_total"))
            for room in room_lines:
                booking_dict = {
                    "name": room.room_id.name,
                    "quantity": room.uom_qty,
                    "price_unit": room.price_unit,
                    "product_type": "room",
                }
                if booking_dict not in account_move_line:
                    if not account_move_line:
                        booking_list.append(booking_dict)
                    else:
                        for rec in account_move_line:
                            if rec["product_type"] == "room":
                                if (
                                    booking_dict["name"] == rec["name"]
                                    and booking_dict["price_unit"] == rec["price_unit"]
                                    and booking_dict["quantity"] != rec["quantity"]
                                ):
                                    booking_list.append(
                                        {
                                            "name": room.room_id.name,
                                            "quantity": booking_dict["quantity"]
                                            - rec["quantity"],
                                            "price_unit": room.price_unit,
                                            "product_type": "room",
                                        }
                                    )
                                else:
                                    booking_list.append(booking_dict)
                    if flag:
                        room.booking_line_visible = True
        if orthotic_lines:
            for orthotic in orthotic_lines:
                booking_list.append(self.create_list(orthotic))
            amount_untaxed_orthotic += sum(orthotic_lines.mapped("price_subtotal"))
            amount_taxed_orthotic += sum(orthotic_lines.mapped("price_tax"))
            amount_total_orthotic += sum(orthotic_lines.mapped("price_total"))
        if service_lines:
            for service in service_lines:
                booking_list.append(self.create_list(service))
            amount_untaxed_service += sum(service_lines.mapped("price_subtotal"))
            amount_taxed_service += sum(service_lines.mapped("price_tax"))
            amount_total_service += sum(service_lines.mapped("price_total"))
        if orthotic_lines:
            for orthotic in orthotic_lines:
                booking_list.append(self.create_list(orthotic))
            amount_untaxed_orthotic += sum(orthotic_lines.mapped("price_subtotal"))
            amount_taxed_orthotic += sum(orthotic_lines.mapped("price_tax"))
            amount_total_orthotic += sum(orthotic_lines.mapped("price_total"))
        if event_lines:
            for event in event_lines:
                booking_list.append(self.create_list(event))
            amount_untaxed_event += sum(event_lines.mapped("price_subtotal"))
            amount_taxed_event += sum(event_lines.mapped("price_tax"))
            amount_total_event += sum(event_lines.mapped("price_total"))
        for rec in self:
            rec.amount_untaxed = (
                amount_untaxed_orthotic
                + amount_untaxed_room
                + amount_untaxed_orthotic
                + amount_untaxed_event
                + amount_untaxed_service
            )
            rec.amount_untaxed_orthotic = amount_untaxed_orthotic
            rec.amount_untaxed_room = amount_untaxed_room
            rec.amount_untaxed_orthotic = amount_untaxed_orthotic
            rec.amount_untaxed_event = amount_untaxed_event
            rec.amount_untaxed_service = amount_untaxed_service
            rec.amount_tax = (
                amount_taxed_orthotic
                + amount_taxed_room
                + amount_taxed_orthotic
                + amount_taxed_event
                + amount_taxed_service
            )
            rec.amount_taxed_orthotic = amount_taxed_orthotic
            rec.amount_taxed_room = amount_taxed_room
            rec.amount_taxed_orthotic = amount_taxed_orthotic
            rec.amount_taxed_event = amount_taxed_event
            rec.amount_taxed_service = amount_taxed_service
            rec.amount_total = (
                amount_total_orthotic
                + amount_total_room
                + amount_total_orthotic
                + amount_total_event
                + amount_total_service
            )
            rec.amount_total_orthotic = amount_total_orthotic
            rec.amount_total_room = amount_total_room
            rec.amount_total_orthotic = amount_total_orthotic
            rec.amount_total_event = amount_total_event
            rec.amount_total_service = amount_total_service
        return booking_list

    #     action check-in
    def action_checkin(self):
        pass

    # action maintenance request
    def action_maintenance_request(self):
        pass

    # amount total
    def _compute_amount_untaxed(self):
        pass

    def action_done(self):
        pass

    def action_checkout(self):
        pass

    def action_invoice(self):
        pass
