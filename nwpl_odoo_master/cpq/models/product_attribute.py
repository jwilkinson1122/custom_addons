import logging
 
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from ..helpers.cpq_custom_field_utils import CPQCustomFieldMixin
from ..hooks import cleanup_orphaned_product_attr_vals

_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"
    _order = "sequence"

    linked_cpq_attribute_id = fields.Many2one(
        "cpq.attribute",
        string="Linked Custom Attribute",
        help="If set, this product attribute can be used to create Custom attribute values from its options."
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
    
    cpq_sync_block = fields.Boolean(compute=False)  

    def _ensure_linked_cpq(self):
        """Ensure each product.attribute in `self` has a linked cpq.attribute.
        Safe for empty, single, or multi recordsets.
        """
        Param = self.env["ir.config_parameter"].sudo()
        if Param.get_param("cpq.sync_from_product") not in ("1", "True", "true", True):
            return self.env["cpq.attribute"].browse()

        CPQAttr = self.env["cpq.attribute"].sudo()
        linked = CPQAttr.browse()

        for attr in self:
            cpq = getattr(attr, "linked_cpq_attribute_id", False)
            if not cpq:
                cpq = CPQAttr.search([("name", "=", attr.name)], limit=1)
                if not cpq:
                    cpq = CPQAttr.create({"name": attr.name})
                attr.with_context(cpq_sync_silent=True).write({"linked_cpq_attribute_id": cpq.id})
            linked |= cpq
        return linked

    def _cpq_refresh_linked(self):
        """Refresh name (and future fields) on already-linked cpq.attribute."""
        for pa in self.sudo():
            cpq = pa.linked_cpq_attribute_id
            if not cpq:
                continue
            updates = {}
            if cpq.name != pa.name:
                updates["name"] = pa.name
            if updates:
                cpq.with_context(cpq_sync_silent=True).sudo().write(updates)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._ensure_linked_cpq()
        return recs

    def unlink(self):
        PTAV = self.env['product.template.attribute.value'].sudo()

        for attr in self:
            broken_ptavs = PTAV.search([('attribute_id', '=', attr.id)])
            if broken_ptavs:
                _repaired = False
                for ptav in broken_ptavs:
                    if not ptav.attribute_id.exists():
                        ptav.unlink()
                        _repaired = True

                if _repaired:
                    _logger = self.env['ir.logging']._get_logger(__name__)
                    _logger.warning("Removed orphaned PTAVs linked to attribute ID %s", attr.id)

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
    
    @api.model
    def backfill_cpq_value_links(self, limit=5000):
        return self.env["cpq.sync.service"].backfill_cpq_value_links(limit=limit)
    
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
    
    linked_cpq_value_id = fields.Many2one(
        "cpq.attribute.value",
        string="Linked CPQ Value",
        index=True,
        ondelete="set null",
        help="Reverse link to the CPQ value"
    )

    cpq_options_relaxed_validation = fields.Boolean(
        default=False,
        string="Relax Options Validation",
        help="Allow a options record to be moved between parents",
    )
    
    def _ensure_linked_cpq_value(self):
        """Ensure each product.attribute.value in `self` has a linked cpq.attribute.value."""
        Param = self.env["ir.config_parameter"].sudo()
        if Param.get_param("cpq.sync_from_product") not in ("1", "True", "true", True):
            return self.env["cpq.attribute.value"].browse()

        CPQVal = self.env["cpq.attribute.value"].sudo()
        linked_vals = CPQVal.browse()

        for pav in self:
            cpq_attr = pav.attribute_id._ensure_linked_cpq()
            if cpq_attr and cpq_attr._name == "cpq.attribute":
                cpq_attr = cpq_attr  
            else:
                cpq_attr = pav.attribute_id.linked_cpq_attribute_id

            if not cpq_attr:
                continue

            cpq_val = getattr(pav, "linked_cpq_value_id", False)
            if not cpq_val:
                cpq_val = CPQVal.search([
                    ("attribute_id", "=", cpq_attr.id),
                    ("name", "=", pav.name),
                ], limit=1)
                if not cpq_val:
                    cpq_val = CPQVal.create({
                        "attribute_id": cpq_attr.id,
                        "name": pav.name,
                    })
                try:
                    pav.with_context(cpq_sync_silent=True).write({"linked_cpq_value_id": cpq_val.id})
                except Exception:
                    pass
            linked_vals |= cpq_val
        return linked_vals
    
    def _cpq_refresh_linked_values(self):
        """
        Refresh name/image on already-linked cpq.attribute.value.
        Mirrors `value.name` and (if present) PAV.image_128 -> CPQ image_128.
        """
        for pav in self.sudo():
            cpqv = pav.linked_cpq_value_id
            if not cpqv:
                continue

            updates = {}
            if cpqv.name != pav.name:
                updates["name"] = pav.name

            if "image_128" in cpqv._fields and ("image_1920" in self._fields or "image_128" in self._fields):
                src = getattr(pav, "image_1920", False) or getattr(pav, "image_128", False)
                if src and not getattr(cpqv, "image_128", False):
                    updates["image_128"] = src


            if updates:
                cpqv.with_context(cpq_sync_silent=True).sudo().write(updates)
        return True
    
    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._ensure_linked_cpq_value()
        return recs

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.setdefault("name", _("%s (copy)") % self.name)
        return super().copy(default=default)
    
    def unlink(self):
        for pav in self:
            cpqv = pav.linked_cpq_value_id
            if cpqv and "linked_product_attribute_value_id" in cpqv._fields:
                try:
                    cpqv.with_context(cpq_sync_silent=True).write({"linked_product_attribute_value_id": False})
                except Exception:
                    pass
        return super().unlink()
    
class ProductAttributeCustomValue(models.Model):
    _inherit = "product.product.cpq.custom.value"

    @api.depends("ptav_id.display_name", "custom_value")
    def _compute_name(self):
        res = super()._compute_name()
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

    x_virtual_cpq_id = fields.Char(
        string="Virtual Custom ID",
        index=True,
        help="ID used to match against Custom attribute value"
    )

    def _cpq_get_combination_info(self):
        self.ensure_one()
        res = super()._cpq_get_combination_info()
        res.update({
            "id": self.id,
            "name": self.name,
            "html_color": self.html_color,
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


   