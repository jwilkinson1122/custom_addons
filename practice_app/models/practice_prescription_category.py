from odoo import api, fields, models


class PrescriptionCategory(models.Model):
    _name = "practice.prescription.category"
    _description = "Prescription Category"
    _parent_store = True

    name = fields.Char(translate=True, required=True)
    # Hierarchy fields
    parent_id = fields.Many2one(
        "practice.prescription.category",
        "Parent Category",
        ondelete="restrict",
    )
    parent_path = fields.Char(index=True)

    # Optional, but nice to have:
    child_ids = fields.One2many(
        "practice.prescription.category",
        "parent_id",
        "Subcategories",
    )

    highlighted_id = fields.Reference(
        [("practice.prescription", "Prescription"), ("res.partner", "Scriptor")],
        "Category Highlight",
    )
