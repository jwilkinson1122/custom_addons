from odoo import fields, models


class AttributeGroup(models.Model):
    _name = "attribute.group"
    _description = "Attribute Group"
    _order = "sequence"

    name = fields.Char(required=True, translate=True)

    sequence = fields.Integer(
        "Sequence in Set", help="The Group order in his attribute's Set"
    )

    attribute_ids = fields.One2many(
        "attribute.attribute", "attribute_group_id", "Attributes"
    )

    model_id = fields.Many2one("ir.model", "Model", required=True, ondelete="cascade")
