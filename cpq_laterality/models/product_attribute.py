from odoo import api, fields, models
from odoo.osv import expression


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.product.cpq.custom.value"

    @api.depends("ptav_id.display_name", "custom_value")
    def _compute_name(self):
        res = super()._compute_name()
        # XXX: This is horrific. This needs to be sorted.
        for record in self.filtered(lambda v: v.ptav_id.cpq_custom_type == "laterality"):
            laterality_id = self.env["cpq.laterality"].browse(int(record.custom_value))
            record.name = f"{record.ptav_id.display_name}: {laterality_id.display_name}"
        return res


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    cpq_custom_type = fields.Selection(
        selection_add=[
            ("laterality", "Laterality"),
        ]
    )

    cpq_laterality_id = fields.Many2one(
        comodel_name="cpq.laterality",
        string="Laterality",
        domain="[('is_leaf', '=', False)]",
    )

    cpq_laterality_relaxed_validation = fields.Boolean(
        default=False,
        string="Relax Laterality Validation",
        help="Allow a laterality record to be moved between parents",
    )

    def _cpq_sanitise_laterality_domain(self, domain):
        self.ensure_one()
        if not self.cpq_laterality_relaxed_validation:
            return expression.AND(
                [
                    domain,
                    [
                        ("parent_id", "child_of", self.cpq_laterality_id.id),
                        ("is_leaf", "=", True),
                    ],
                ]
            )

        return domain

    def _cpq_cast_custom_laterality(self, value):
        try:
            return self.env["cpq.laterality"].search(
                self._cpq_sanitise_laterality_domain(
                    [
                        ("id", "=", int(value)),
                    ]
                )
            )
        except (ValueError, TypeError):
            return self.env["cpq.laterality"]

    def _cpq_sanitise_custom_laterality(self, value):
        try:
            return (
                self.env["cpq.laterality"]
                .search(
                    self._cpq_sanitise_laterality_domain(
                        [
                            ("id", "=", int(value)),
                        ]
                    )
                )
                .id
            )
        except (ValueError, TypeError):
            return False

    def _cpq_validate_custom_laterality(self, value):
        try:
            value_as_int = int(value)
        except (ValueError, TypeError):
            return False

        count = self.env["cpq.laterality"].search_count(
            self._cpq_sanitise_laterality_domain(
                [
                    ("id", "=", value_as_int),
                ]
            )
        )
        return count == 1


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    cpq_laterality_id = fields.Many2one(
        related="product_attribute_value_id.cpq_laterality_id"
    )

    def _cpq_get_combination_info(self):
        res = super()._cpq_get_combination_info()
        if self.is_custom and self.cpq_custom_type == "laterality":
            lateralitys = self.env["cpq.laterality"].search(
                [
                    ("parent_id", "child_of", self.cpq_laterality_id.id),
                    ("is_leaf", "=", True),
                ]
            )
            res.update(
                {
                    "cpq_selection_values": [
                        (laterality.id, laterality.display_name) for laterality in lateralitys
                    ]
                }
            )

        return res
