from odoo import fields, models


class PrescriptionAmenity(models.Model):
    """Model that handles all amenities of the prescription/ fasilitas prescription"""

    _name = "prescription.amenity"
    _description = "Prescription Amenity"
    _inherit = "mail.thread"
    _order = "id desc"

    name = fields.Char(string="Name", help="Name of the amenity")
    icon = fields.Image(string="Icon", required=True, help="Image of the amenity")
    description = fields.Html(string="About", help="Specify the amenity description")
