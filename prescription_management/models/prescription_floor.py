from odoo import fields, models


class PrescriptionFLoor(models.Model):
    """Model That holds the prescription floors."""

    _name = "prescription.floor"
    _description = "Floor"
    _order = "id desc"

    name = fields.Char(string="Name", help="Name of the floor", required=True)
    user_id = fields.Many2one(
        "res.users", string="Manager", help="Manager of the floor", required=True
    )
