import logging
from odoo import models
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class CPQCustomFieldMixin(models.AbstractModel):
    _name = "cpq.custom.field.mixin"
    _description = "Reusable Custom Custom Field Logic"

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
                        ("parent_id", "child_of", self.linked_option_id.id),
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
    
 