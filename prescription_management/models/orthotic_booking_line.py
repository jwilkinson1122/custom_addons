# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class OrthoticBooking(models.Model):
    _name = "orthotic.booking"
    _description = "Prescription Orthotic Line"
    _rec_name = "orthotic_id"

    @tools.ormcache()
    def _get_default_uom_id(self):
        """method for getting the default uom id"""
        return self.env.ref("uom.product_uom_unit")

    booking_id = fields.Many2one(
        "room.booking",
        string="Booking",
        help="Shows the room Booking",
        ondelete="cascade",
    )
    orthotic_id = fields.Many2one(
        "prescription.product", string="Product", help="Indicates the orthotic Product"
    )
    description = fields.Char(
        string="Description",
        help="Description of Orthotic Product",
        related="orthotic_id.display_name",
    )
    uom_qty = fields.Float(
        string="qty",
        default=1,
        help="The quantity converted into the UoM used by the product",
    )
    uom_id = fields.Many2one(
        "uom.uom",
        readonly=True,
        string="Unit of Measure",
        default=_get_default_uom_id,
        help="This will set " "the unit of" " measure used",
    )


# class OrthoticBookingLine(models.Model):
#     _inherit = "orthotic.booking.line"
#     _description = "Orthotic Booking Line"
#     _rec_name = "orthotic_id"

#     @tools.ormcache()
#     def _get_default_uom_id(self):
#         return self.env.ref("uom.product_uom_km")

#     booking_id = fields.Many2one(
#         "room.booking",
#         string="Booking",
#         help="Shows the room Booking",
#         ondelete="cascade",
#     )
#     orthotic_id = fields.Many2one(
#         "orthotic.model", string="Vehicle", help="Indicates the orthotic"
#     )
#     description = fields.Char(
#         string="Description",
#         help="Description of Vehicle",
#         related="orthotic_id.displayname",
#     )
#     uom_qty = fields.Float(
#         string="qty",
#         default=1,
#         help="The quantity converted into the UoM used by the product",
#     )
#     uom_id = fields.Many2one(
#         "uom.uom",
#         readonly=True,
#         string="Unit of Measure",
#         default=_get_default_uom_id,
#         help="This will set the unit of measure used",
#     )
#     price_unit = fields.Float(
#         related="orthotic_id.price_per_km", string="Rent KM", digits="Product Price"
#     )
#     tax_ids = fields.Many2many(
#         "account.tax",
#         "orthotic_order_line_taxes_rel",
#         "orthotic_id",
#         "tax_id",
#         related="orthotic_id.taxes_id",
#         string="Taxes",
#         domain=[("type_tax_use", "=", "sale")],
#     )
#     currency_id = fields.Many2one(
#         string="Currency", related="booking_id.pricelist_id.currency_id"
#     )
#     price_subtotal = fields.Float(
#         string="Subtotal",
#         compute="_compute_price_subtotal",
#         help="Total Price Excluding Tax",
#         store=True,
#     )
#     price_tax = fields.Float(
#         string="Total Tax",
#         compute="_compute_price_subtotal",
#         help="Tax amount",
#         store=True,
#     )
#     price_total = fields.Float(
#         string="Total", compute="_compute_price_subtotal", store=True
#     )
#     state = fields.Selection(
#         related="booking_id.state", string="Order Status", copy=False
#     )

#     @api.depends("uom_qty", "price_unit", "tax_ids")
#     def _compute_price_subtotal(self):
#         for line in self:
#             tax_results = ["account.tax"]._compute_taxes(
#                 [line._convert_to_tax_base_line_dict()]
#             )
#             totals = list(tax_results["totals"].values())[0]
#             amount_untaxed = totals["amount_untaxed"]
#             amount_tax = totals["amount_tax"]
#             line.update(
#                 {
#                     "price_subtotal": amount_untaxed,
#                     "price_tax": amount_tax,
#                     "price_total": amount_untaxed + amount_tax,
#                 }
#             )
#             if self.env.context.get(
#                 "import_file", False
#             ) and not self.env.user.user_has_groups("account.group_account_manager"):
#                 line.tax_id.invalidate_recordset(["invoice_repartition_line_ids"])

#     def _convert_to_tax_base_line_dict(self):
#         self.ensure_one()
#         return self.env["account.tax"]._convert_to_tax_base_line_dict(
#             self,
#             partner=self.booking_id.partner_id,
#             currency=self.currency_id,
#             taxes=self.tax_ids,
#             price_unit=self.price_unit,
#             quantity=self.uom_qty,
#             price_subtotal=self.price_subtotal,
#         )

#     def search_available_orthotic(self):
#         return self.env["orthotic.model"].search(
#             [("id", "in", self.search([]).mapped("orthotic_id").ids)].ids
#         )
