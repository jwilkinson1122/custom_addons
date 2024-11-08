from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class PrescriptionRoom(models.Model):
    """Model That holds All details regarding prescription room"""

    _name = "prescription.room"
    _description = "rooms"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @tools.ormcache()
    def _get_default_uom_id(self):
        """Method for getting the default uom id"""
        return self.env.ref("uom.product_uom_unit")

    name = fields.Char(
        string="name",
        help="Name of the Room",
        index="trigram",
        required=True,
        translate=True,
    )
    status = fields.Selection(
        [
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("occupied", "Occupied"),
        ],
        default="available",
        string="Status",
        help="Status of the Room",
        tracking=True,
    )
    is_room_avail = fields.Boolean(
        string="Available", default=True, help="Check If the room is available"
    )
    list_price = fields.Float(
        string="Rent", digits="Product Price", help="The rent of the Room"
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit Of Measure",
        default=_get_default_uom_id,
        required=True,
        help="Default unit of measure used for all stock" " operations.",
    )
    room_image = fields.Image(
        string="Room Image", max_width=1920, max_height=1920, help="Image of the room"
    )
    # taxes_ids = fields.Many2one('account.tax', 'prescription_room_taxes_rel', 'room_id', 'tax_id', help='Default taxes used when selling the''room', string='Customer Taxes', domain=[('type_tax_use', '=', 'sale')], default=lambda self: self.env.company.account_sale_tax.id)
    # room_amenities_ids = fields.Many2one("prescription.amenity", string='Room Amenities', help='List of room amenities')
    floor_id = fields.Many2one(
        "prescription.floor",
        string="FLoor",
        help="Automatically selects the manager",
        tracking=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        related="floor_id.user_id",
        help="Automatically selects the manager",
    )
    room_type = fields.Selection(
        [("single", "Single"), ("double", "Double"), ("dormitory", "Dormitory")],
        required=True,
        string="Room Type",
        help="Automatically selects the room Type",
        tracking=True,
        default="single",
    )
    num_person = fields.Integer(
        string="Number Of Persons",
        required=True,
        help="Automatically chooses the No. Of persons",
        tracking=True,
    )
    description = fields.Html(
        string="Description", help="Add Description", translate=True
    )
