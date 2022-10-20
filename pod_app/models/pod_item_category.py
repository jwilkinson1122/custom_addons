from odoo import api, fields, models


class ItemCategory(models.Model):
    _name = "pod.item.category"
    _description = "Item Category"
    _parent_store = True

    name = fields.Char(translate=True, required=True)
    # Hierarchy fields
    parent_id = fields.Many2one(
        "pod.item.category",
        "Parent Category",
        ondelete="restrict",
    )
    parent_path = fields.Char(index=True)

    # Optional, but nice to have:
    child_ids = fields.One2many(
        "pod.item.category",
        "parent_id",
        "Subcategories",
    )

    highlighted_id = fields.Reference(
        [("pod.item", "Item"), ("res.partner", "Author")],
        "Category Highlight",
    )
