from odoo import fields, models


class AccountMove(models.Model):
    """Inherited account move for adding prescription boong reference field to invoicing model"""

    _inherit = "account.move"

    prescription_booking_id = fields.Many2one(
        "room.booking",
        string="Booking Reference",
        readonly=True,
        help="Choose the Booking reference",
    )
