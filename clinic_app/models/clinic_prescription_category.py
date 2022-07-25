from odoo import api, fields, models


class PrescriptionCategory(models.Model):
    _name = "clinic.prescription.category"
    _description = "Prescription Category"
    _parent_store = True

    name = fields.Char(translate=True, required=True)
    # Hierarchy fields
    parent_id = fields.Many2one(
        "clinic.prescription.category",
        "Parent Category",
        ondelete="restrict",
    )
    parent_path = fields.Char(index=True)

    # Optional, but nice to have:
    child_ids = fields.One2many(
        "clinic.prescription.category",
        "parent_id",
        "Subcategories",
    )

    highlighted_id = fields.Reference(
        [("clinic.prescription", "Prescription"), ("res.partner", "Doctor")],
        "Category Highlight",
    )
