# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ProductAttribute(models.Model):
    _inherit = "product.attribute.value"

    cpq_allow_dynamic_bom_quantity = fields.Boolean(
        compute="_compute_cpq_allow_dynamic_bom_quantity", store=True
    )

    @api.depends("is_custom", "cpq_custom_type")
    def _compute_cpq_allow_dynamic_bom_quantity(self):
        for record in self:
            record.cpq_allow_dynamic_bom_quantity = (
                record.is_custom and record.cpq_custom_type in ("integer", "float")
            )

class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    cpq_allow_dynamic_bom_quantity = fields.Boolean(
        related="product_attribute_value_id.cpq_allow_dynamic_bom_quantity",
        store=True,
        index=True,
    )

class ProductTemplate(models.Model):
    _inherit = "product.template"

    cpq_dynamic_bom_ids = fields.One2many("cpq.dynamic.bom", "product_tmpl_id")
    cpq_dynamic_bom_count = fields.Integer(
        compute="_compute_cpq_dynamic_bom_count", store=True
    )

    def _cpq_tooltip_items(self):
        self.ensure_one()
        res = super()._cpq_tooltip_items()
        res.extend(
            [
                _(
                    "Custom Products can be used in conjunction with"
                    " Configurable Dynamic BoMs to generate kits and manufacturing"
                    " orders dynamically, on-demand."
                ),
            ]
        )

        if self.bom_count > 0 and self.cpq_dynamic_bom_count > 0:
            res.extend(
                [
                    "<b class='text-danger'>{}</b>".format(
                        _(
                            "You have both Standard and Configurable BoMs"
                            " configured! This will result in inconsistent BoM"
                            " handling!"
                        )
                    )
                ]
            )

        return res

    @api.depends("cpq_ok", "bom_ids", "cpq_dynamic_bom_ids")
    def _compute_cpq_tooltip(self):
        return super()._compute_cpq_tooltip()

    @api.constrains("attribute_line_ids")
    def _check_product_with_component_change_allowed(self):
        for rec in self:
            if not rec.attribute_line_ids:
                continue
            for bom in rec.bom_ids:
                for line in bom.bom_line_ids.filtered("match_on_attribute_ids"):
                    prod_attr_ids = rec.attribute_line_ids.attribute_id.filtered(
                        lambda x: x.create_variant != "no_variant"
                    ).ids
                    comp_attr_ids = line.match_on_attribute_ids.ids
                    diff_ids = list(set(comp_attr_ids) - set(prod_attr_ids))
                    diff = rec.env["product.attribute"].browse(diff_ids)
                    if diff:
                        raise UserError(
                            _(
                                "The attributes you're trying to remove are used in "
                                "the BoM as a match with Component (Product Template). "
                                "To remove these attributes, first remove the BOM line "
                                "with the matching component.\n"
                                "Attributes: %(attributes)s\nBoM: %(bom)s",
                                attributes=", ".join(diff.mapped("name")),
                                bom=bom.display_name,
                            )
                        )

    @api.constrains("attribute_line_ids")
    def _check_component_change_allowed(self):
        for rec in self:
            if not rec.attribute_line_ids:
                continue
            boms = self._get_component_boms()
            if not boms:
                continue
            for bom in boms:
                vpa = bom.product_tmpl_id.valid_product_template_attribute_line_ids
                prod_attr_ids = vpa.attribute_id.ids
                comp_attr_ids = self.attribute_line_ids.attribute_id.ids
                diff = list(set(comp_attr_ids) - set(prod_attr_ids))
                if len(diff) > 0:
                    attr_recs = self.env["product.attribute"].browse(diff)
                    raise UserError(
                        _(
                            "This product template is used as a component in the "
                            "BOMs for %(bom)s and attribute(s) %(attributes)s is "
                            "not present in all such product(s), and this would "
                            "break the BOM behavior.",
                            attributes=", ".join(attr_recs.mapped("name")),
                            bom=bom.display_name,
                        )
                    )

    def _get_component_boms(self):
        self.ensure_one()
        bom_lines = self.env["mrp.bom.line"].search(
            [("component_template_id", "=", self._origin.id)]
        )
        if bom_lines:
            return bom_lines.mapped("bom_id")
        return False



    @api.depends("cpq_ok", "cpq_dynamic_bom_ids", "cpq_dynamic_bom_ids.active")
    def _compute_cpq_dynamic_bom_count(self):
        for record in self:
            if not record.cpq_ok:
                record.cpq_dynamic_bom_count = 0
                continue
            record.cpq_dynamic_bom_count = len(record.cpq_dynamic_bom_ids)

    def action_view_cpq_dynamic_bom(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Custom Products Bill of Materials"),
            "res_model": "cpq.dynamic.bom",
            "view_mode": "form",
            "res_id": self.cpq_dynamic_bom_ids.id,
        }

    def write(self, vals):
        if not self.env.context.get("cpq_mrp_skip_auto_archive", False):
            if vals.get("cpq_ok") is False:
                for record in self.sudo().filtered(
                    lambda p: p.cpq_ok and p.cpq_dynamic_bom_ids
                ):
                    record.cpq_dynamic_bom_ids.message_post(
                        body=_(
                            "Archived due product template not longer being \
                                configurable"
                        )
                    )
                    record.cpq_dynamic_bom_ids.write({"active": False})

            if vals.get("active") is False:
                for record in self.sudo().filtered(
                    lambda p: p.active and p.cpq_dynamic_bom_ids
                ):
                    record.cpq_dynamic_bom_ids.message_post(
                        body=_("Archived due to product template being archived")
                    )
                    record.cpq_dynamic_bom_ids.write({"active": False})

        return super().write(vals)
