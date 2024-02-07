
from odoo import fields, models


class PrescriptionTag(models.Model):
    _description = "Prescription Tags"
    _name = "prescription.tag"
    _order = "name"

    active = fields.Boolean(
        default=True,
        help="The active field allows you to hide the category without " "removing it.",
    )
    name = fields.Char(
        string="Tag Name",
        required=True,
        translate=True,
        copy=False,
    )
    is_public = fields.Boolean(
        string="Public Tag",
        help="The tag is visible in the portal view",
    )
    color = fields.Integer(string="Color Index")
    prescription_ids = fields.Many2many(comodel_name="prescription")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists !"),
    ]
