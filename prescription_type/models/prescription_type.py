from odoo import fields, models


class PrescriptionType(models.Model):
    _name = "prescription.type"
    _description = "Prescription Type"

    name = fields.Char("Prescription Type Name", copy=False, required=True)
    source_location_id = fields.Many2one(
        "stock.location",
        "Source Location",
        help="This is the location where the product to prescription is located.",
    )
    source_location_add_part_id = fields.Many2one(
        "stock.location",
        "Source Location Add Component",
        help="This is the location where the part of the product to add is located.",
    )
    destination_location_add_part_id = fields.Many2one(
        "stock.location",
        "Destination Location Add Component",
        help="This is the location where the part of the product to add is located.",
    )
    source_location_remove_part_id = fields.Many2one(
        "stock.location",
        "Source Location Remove Component",
        help="This is the location where the part of the product to remove is located.",
    )
    destination_location_remove_part_id = fields.Many2one(
        "stock.location",
        "Destination Location Remove Component",
        help="This is the location where the part of the product to remove is located.",
    )
