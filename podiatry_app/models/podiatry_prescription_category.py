from odoo import api, fields, models


class PrescriptionCategory(models.Model):
    _name = "podiatry.prescription.category"
    _description = "Prescription Category"
    _parent_store = True

    name = fields.Char(translate=True, required=True)
    # Hierarchy fields
    parent_id = fields.Many2one(
        "podiatry.prescription.category",
        "Parent Category",
        ondelete="restrict",
    )
    parent_path = fields.Char(index=True)

    # Optional, but nice to have:
    child_ids = fields.One2many(
        "podiatry.prescription.category",
        "parent_id",
        "Subcategories",
    )

    highlighted_id = fields.Reference(
        [("podiatry.prescription", "Prescription"), ("res.partner", "Author")],
        "Category Highlight",
    )
