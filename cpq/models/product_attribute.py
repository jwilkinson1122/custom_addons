import logging
 
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
# from .cpq_custom_field_utils import CPQCustomFieldMixin
from ..helpers.cpq_custom_field_utils import CPQCustomFieldMixin
from ..hooks import cleanup_orphaned_product_attr_vals

_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"
    _order = "sequence"

    linked_cpq_attribute_id = fields.Many2one(
        "cpq.attribute",
        string="Linked CPQ Attribute",
        help="If set, this product attribute can be used to create CPQ attribute values from its options."
    )
    
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

    active = fields.Boolean(default=True, string="Active")
    cpq_propagate_to_variant = fields.Boolean(
        string="Propagate to the Variant",
        default=False,
    )

    # def unlink(self):
    #     for attr in self:
    #         ptavs = self.env['product.template.attribute.value'].search([
    #             ('attribute_id', '=', attr.id)
    #         ])
    #         if ptavs:
    #             ptavs.unlink() 
    #     return super().unlink()

    def unlink(self):
        PTAV = self.env['product.template.attribute.value'].sudo()

        for attr in self:
            # Step 1: Repair orphaned PTAVs by checking if their attribute still exists
            broken_ptavs = PTAV.search([('attribute_id', '=', attr.id)])
            if broken_ptavs:
                _repaired = False
                for ptav in broken_ptavs:
                    if not ptav.attribute_id.exists():
                        ptav.unlink()
                        _repaired = True

                if _repaired:
                    _logger = self.env['ir.logging']._get_logger(__name__)
                    _logger.warning("🔧 Removed orphaned PTAVs linked to attribute ID %s", attr.id)

            # Step 2: Check again — block deletion if active links remain
            remaining = PTAV.search_count([('attribute_id', '=', attr.id)])
            if remaining:
                raise UserError(f"Cannot delete attribute '{attr.name}' — still linked to {remaining} PTAV(s).")

        return super().unlink()
    
    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if "name" not in default:
            default["name"] = _("%s (copy)") % (self.name)
        return super().copy(default=default)
    
class ProductAttributeValue(models.Model, CPQCustomFieldMixin):  
    _inherit = "product.attribute.value"

    active = fields.Boolean(default=True)
    cpq_custom_type = fields.Selection([
        ("integer", "Integer"),
        ("float", "Float"),
        ("char", "Text"),
        ("many2one", "Many2one"),
        ("options", "Option"),
    ], string="Custom Input Type")

    linked_option_id = fields.Many2one(
        comodel_name="product.options",
        string="Linked Option",
        domain="[('is_leaf', '=', True)]"
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
        default.setdefault("name", _("%s (copy)") % self.name)
        return super().copy(default=default)


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
        related="attribute_id.cpq_propagate_to_variant", store=True, readonly=False
    )
    cpq_custom_type = fields.Selection(
        related="product_attribute_value_id.cpq_custom_type", store=True, readonly=False
    )
    linked_option_id = fields.Many2one(
        related="product_attribute_value_id.linked_option_id", store=True, readonly=False
    )

    # Refactored to remove duplicate code
    def _cpq_get_combination_info(self):
        self.ensure_one()
        res = super()._cpq_get_combination_info()
        res.update({
            "id": self.id,
            "name": self.name,
            "html_color": self.html_color,
            # "is_custom": self.is_custom,
            "is_custom": False if self.linked_option_id else self.is_custom,
            "price_extra": self.price_extra,
            "excluded": False,
            "cpq_custom_type": self.cpq_custom_type,
        })

        if self.is_custom and self.cpq_custom_type == "options":
            options = self.env["product.options"].search([
                ("parent_id", "child_of", self.linked_option_id.id),
                ("is_leaf", "=", True),
            ])
            res["cpq_selection_values"] = [(opt.id, opt.display_name) for opt in options]

        return res

    def cleanup_ptavs_ui(self):
        env = self.env
        count = cleanup_orphaned_product_attr_vals(env)
        raise UserError("Cleanup complete.\nDeleted %s orphaned PTAV(s)." % count)
   
    @api.model
    def clean_orphaned_records(self):
        broken_attr = self.search([('attribute_id', '!=', False)]).filtered(lambda r: not r.attribute_id.exists())
        broken_value = self.search([('product_attribute_value_id', '!=', False)]).filtered(lambda r: not r.product_attribute_value_id.exists())

        count_attr = len(broken_attr)
        count_value = len(broken_value)

        if count_attr or count_value:
            _logger.warning("Found %s PTAVs with broken attribute_id and %s with broken product_attribute_value_id.", count_attr, count_value)
            _logger.debug("Broken attribute_id PTAVs: %s", broken_attr.mapped("name"))
            _logger.debug("Broken product_attribute_value_id PTAVs: %s", broken_value.mapped("name"))

            (broken_attr | broken_value).unlink()
            _logger.info("Orphaned PTAVs removed.")
        else:
            _logger.info("No orphaned PTAVs found.")

        return {
            "broken_attribute_ids": count_attr,
            "broken_value_ids": count_value,
            "total_removed": count_attr + count_value,
        }


    # @classmethod
    # def clean_orphaned_records(cls):
    #     broken = cls.search([
    #         '|',
    #         ('attribute_id', '=', False),
    #         ('product_attribute_value_id', '=', False),
    #     ])
    #     if broken:
    #         _logger.warning("Found %s orphaned PTAVs. Removing them.", len(broken))
    #         _logger.debug("Orphaned PTAV names: %s", broken.mapped("name"))
    #         broken.unlink()
    #         _logger.info("Orphaned PTAVs removed.")
    #     else:
    #         _logger.info("No orphaned PTAVs found.")

    # @api.model
    # def clean_orphaned_records(self):
    #     orphans = self.search([('attribute_id', '!=', False)]).filtered(lambda r: not r.attribute_id.exists())
    #     count = len(orphans)
    #     if count:
    #         orphans.unlink()
    #     return count