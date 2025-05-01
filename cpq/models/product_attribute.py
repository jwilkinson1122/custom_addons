from odoo import _, api, fields, models
from odoo.osv import expression


class ProductAttribute(models.Model):
    _inherit = "product.attribute"
    _order = "sequence"

    create_variant = fields.Selection(
        selection=[
            ('always', 'Instantly'),
            ('dynamic', 'Dynamically'),
            ('no_variant', 'Never (option)'),
        ],
        default='no_variant',
        string="Variants Creation Mode",
        help="""- Instantly: All possible variants are created as soon as the attribute and its values are added to a product.
        - Dynamically: Each variant is created only when its corresponding attributes and values are added to a sales order.
        - Never: Variants are never created for the attribute.
        Note: the variants creation mode cannot be changed once the attribute is used on at least one product.""",
        required=True)
    # display_type = fields.Selection(
    #     selection=[
    #         ('radio', 'Radio'),
    #         ('pills', 'Pills'),
    #         ('select', 'Select'),
    #         ('color', 'Color'),
    #         ('multi', 'Multi-checkbox (option)'),
    #     ],
    #     default='radio',
    #     required=True,
    #     help="The display type used in the Product Configurator.")

    active = fields.Boolean(default=True, string="Active")
    cpq_propagate_to_variant = fields.Boolean(
        string="Propagate to the Variant",
        default=False,
    )

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if "name" not in default:
            default["name"] = _("%s (copy)") % (self.name)
        return super().copy(default=default)


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    active = fields.Boolean(
        default=True,
    )

    # cpq_custom_type = fields.Selection(
    #     selection_add=[
    #         ("options", "Options"),
    #     ]
    # )

    cpq_custom_type = fields.Selection(
        [
            ("integer", "Integer"),
            ("float", "Float"),
            ("char", "Text"),
            ("many2one", "Many2one"),
            ("options", "Option"),
        ],
        string="Configurable custom type",
    )

    cpq_options_id = fields.Many2one(
        comodel_name="product.options",
        string="Option",
        domain="[('is_leaf', '=', False)]",
    )

    cpq_options_relaxed_validation = fields.Boolean(
        default=False,
        string="Relax Options Validation",
        help="Allow a options record to be moved between parents",
    )

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if "name" not in default:
            default["name"] = _("%s (copy)") % (self.name)
        return super().copy(default=default)

    def _cpq_cast_custom(self, value):
        """
        Cast the stored custom_value into the real value.
        i.e. custom_value may store a int, which we need to cast into an Odoo
        record
        """
        self.ensure_one()

        if not self.is_custom or not self.cpq_custom_type:
            return value

        method = f"_cpq_cast_custom_{self.cpq_custom_type}"
        return getattr(self, method)(value)

    def _cpq_cast_custom_options(self, value):
        try:
            return self.env["product.options"].search(
                self._cpq_sanitise_options_domain(
                    [
                        ("id", "=", int(value)),
                    ]
                )
            )
        except (ValueError, TypeError):
            return self.env["product.options"]

    def _cpq_cast_custom_integer(self, value):
        return self._cpq_sanitise_custom_integer(value)

    def _cpq_cast_custom_float(self, value):
        return self._cpq_sanitise_custom_integer(value)

    def _cpq_cast_custom_char(self, value):
        return self._cpq_sanitise_custom_char(value)

    def _cpq_cast_custom_many2one(self, _value):
        return NotImplementedError()

    def _cpq_sanitise_custom(self, value):
        self.ensure_one()

        if not self.is_custom or not self.cpq_custom_type:
            return value

        method = f"_cpq_sanitise_custom_{self.cpq_custom_type}"
        return getattr(self, method)(value)

    def _cpq_sanitise_options_domain(self, domain):
        self.ensure_one()
        if not self.cpq_options_relaxed_validation:
            return expression.AND(
                [
                    domain,
                    [
                        ("parent_id", "child_of", self.cpq_options_id.id),
                        ("is_leaf", "=", True),
                    ],
                ]
            )

        return domain

    def _cpq_sanitise_custom_options(self, value):
        try:
            return (
                self.env["product.options"]
                .search(
                    self._cpq_sanitise_options_domain(
                        [
                            ("id", "=", int(value)),
                        ]
                    )
                )
                .id
            )
        except (ValueError, TypeError):
            return False

    def _cpq_sanitise_custom_integer(self, value):
        return int(value)

    def _cpq_sanitise_custom_float(self, value):
        return float(value)

    def _cpq_sanitise_custom_char(self, value):
        if value is None:
            return ""
        return value.strip()

    def _cpq_sanitise_custom_many2one(self, value):
        raise NotImplementedError()

    def _cpq_validate_custom(self, value):
        self.ensure_one()

        if not self.is_custom or not self.cpq_custom_type:
            return True

        method = f"_cpq_validate_custom_{self.cpq_custom_type}"
        return getattr(self, method)(value)

    def _cpq_validate_custom_options(self, value):
        try:
            value_as_int = int(value)
        except (ValueError, TypeError):
            return False

        count = self.env["product.options"].search_count(
            self._cpq_sanitise_options_domain(
                [
                    ("id", "=", value_as_int),
                ]
            )
        )
        return count == 1

    def _cpq_validate_custom_integer(self, value):
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False

    def _cpq_validate_custom_float(self, value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def _cpq_validate_custom_char(self, value):
        return isinstance(value, str) and len(value) > 0

    def _cpq_validate_custom_many2one(self, value):
        raise NotImplementedError()


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.product.cpq.custom.value"

    @api.depends("ptav_id.display_name", "custom_value")
    def _compute_name(self):
        res = super()._compute_name()
        # XXX: This is horrific. This needs to be sorted.
        for record in self.filtered(lambda v: v.ptav_id.cpq_custom_type == "options"):
            options_id = self.env["product.options"].browse(int(record.custom_value))
            record.name = f"{record.ptav_id.display_name}: {options_id.display_name}"
        return res


# class ProductTemplateAttributeLine(models.Model):
#     _inherit = "product.template.attribute.line"

#     def _cpq_get_combination_info_list(self):
#         return [line._cpq_get_combination_info() for line in self]
    
class ProductAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"
    _order = "product_tmpl_id, sequence, id"

    sequence = fields.Integer(default=10)
    cpq_propagate_to_variant = fields.Boolean(
        related="attribute_id.cpq_propagate_to_variant", store=True
    )

    def _cpq_get_combination_info_list(self):
        return [line._cpq_get_combination_info() for line in self]

    def _cpq_get_combination_info(self):
        self.ensure_one()
        i = self

        return {
            "id": i.id,
            "name": i.display_name,
            "display_type": i.attribute_id.display_type,
            "ptav_ids": [
                ptav_id._cpq_get_combination_info()
                for ptav_id in i.product_template_value_ids.filtered(
                    lambda l: l.ptav_active  # noqa: E741
                )
            ],
        }


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    cpq_propagate_to_variant = fields.Boolean(
        related="attribute_id.cpq_propagate_to_variant"
    )
    cpq_custom_type = fields.Selection(
        related="product_attribute_value_id.cpq_custom_type"
    )

    cpq_options_id = fields.Many2one(
        related="product_attribute_value_id.cpq_options_id"
    )

    # Refactored to remove duplicate code
    def _cpq_get_combination_info(self):
        res = super()._cpq_get_combination_info()
        if self.is_custom and self.cpq_custom_type == "options":
            optionss = self.env["product.options"].search(
                [
                    ("parent_id", "child_of", self.cpq_options_id.id),
                    ("is_leaf", "=", True),
                ]
            )
            res.update(
                {
                    "cpq_selection_values": [
                        (options.id, options.display_name) for options in optionss
                    ]
                }
            )

        return res


    def _cpq_get_combination_info(self):
        self.ensure_one()
        ptav_id = self

        return {
            "id": ptav_id.id,
            "name": ptav_id.name,
            "html_color": ptav_id.html_color,
            "is_custom": ptav_id.is_custom,
            "price_extra": ptav_id.price_extra,  # ✅ Fix is here
            "excluded": False,
            "cpq_custom_type": ptav_id.cpq_custom_type,
        }

