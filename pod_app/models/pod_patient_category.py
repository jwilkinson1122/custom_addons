from odoo import api, fields, models


class PatientCategory(models.Model):
    _name = "pod.patient.category"
    _description = "Patient Category"
    _parent_store = True

    name = fields.Char(translate=True, required=True)
    # Hierarchy fields
    parent_id = fields.Many2one(
        "pod.patient.category",
        "Parent Category",
        ondelete="restrict",
    )
    parent_path = fields.Char(index=True)

    # Optional, but nice to have:
    child_ids = fields.One2many(
        "pod.patient.category",
        "parent_id",
        "Subcategories",
    )

    highlighted_id = fields.Reference(
        [("pod.patient", "Patient"), ("res.partner", "Author")],
        "Category Highlight",
    )
