from odoo import api, fields, models


class PrescriptionCategory(models.Model):
    _name = "pod.prescription.category"
    _description = "Prescription Category"
    _parent_store = True

    name = fields.Char(translate=True, required=True)
    # Hierarchy fields
    parent_id = fields.Many2one(
        "pod.prescription.category",
        "Parent Category",
        ondelete="restrict",
    )
    parent_path = fields.Char(index=True)

    # Optional, but nice to have:
    child_ids = fields.One2many(
        "pod.prescription.category",
        "parent_id",
        "Subcategories",
    )

    highlighted_id = fields.Reference(
        [("pod.prescription", "Prescription"), ("res.partner", "Doctor")],
        "Category Highlight",
    )
