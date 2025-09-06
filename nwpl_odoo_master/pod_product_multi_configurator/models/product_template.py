# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import ormcache

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allow_qty_mode = fields.Boolean(default=True)
    
    laterality_enabled = fields.Boolean(default=True)
    
    laterality_default = fields.Selection([
        ('left_only', 'Left Only'),
        ('right_only', 'Right Only'),
        ('bilateral', 'Bilateral'),
    ], default='bilateral')
    
    bilateral_default_type = fields.Selection([
        ('shared', 'Bilateral Shared'),
        ('split', 'Bilateral Split'),
        ('hybrid', 'Bilateral Hybrid'),
    ], default='shared')
    
    attribute_set_id = fields.Many2one(
        "product.attribute.set",
        string="Attribute Set",
        default=lambda self: self._get_default_att_set(),
    )

    def _get_default_att_set(self):
        # Default from category if available
        default_categ = self._get_default_category_id()
        if default_categ:
            categ = self.env["product.category"].browse(default_categ.id)
            return categ.attribute_set_id.id

    def _prefs_ptav_map(self):
        """For each template, map PAV -> PTAV id for quick lookups."""
        self.ensure_one()
        ptavs = self.valid_product_template_attribute_line_ids.mapped("product_template_value_ids")
        return {p.product_attribute_value_id.id: p.id for p in ptavs}

    @ormcache('partner.commercial_partner_id.id', 'product_tmpl.id')
    def _get_preference_payload(self, partner, product_tmpl):
        Rule = self.env["product.config.preference"].sudo()
        rules = Rule.search([
            ("active", "=", True),
            ("partner_id", "child_of", partner.commercial_partner_id.id),
            ("product_tmpl_id", "in", [False, product_tmpl.id]),
        ])
        left_pavs  = {r.pav_id.id for r in rules if r.scope in ("left", "shared") or not r.scope}
        right_pavs = {r.pav_id.id for r in rules if r.scope in ("right", "shared") or not r.scope}
        notes = {(r.pav_id.id, (r.scope or "shared")): (r.note or "") for r in rules}
        return {"left_pavs": left_pavs, "right_pavs": right_pavs, "notes": notes}

    @api.model
    def get_configurator_ptal_payload(self, product_tmpl_id, partner_id=None):
        tmpl = self.sudo().browse(product_tmpl_id).exists()
        if not tmpl:
            return {"ptal_ids": []}

        partner = (self.env["res.partner"].browse(partner_id).commercial_partner_id
                   if partner_id else self.env.user.partner_id.commercial_partner_id)

        pref = self._get_preference_payload(partner, tmpl)  # ← private, server-side only
        left_set, right_set, notes = pref["left_pavs"], pref["right_pavs"], pref["notes"]

        def _note_for(pav_id, side):
            return notes.get((pav_id, side), notes.get((pav_id, "shared"), ""))

        ptal_ids = []
        for ptal in tmpl.valid_product_template_attribute_line_ids:
            values_payload = []
            for ptav in ptal.product_template_value_ids:
                pav_id = ptav.product_attribute_value_id.id
                values_payload.append({
                    "id": ptav.id,
                    "name": ptav.name,
                    "price_extra": ptav.price_extra,
                    "isPreferredLeft":  pav_id in left_set,
                    "isPreferredRight": pav_id in right_set,
                    "isPreferred": (pav_id in left_set) or (pav_id in right_set),
                    "noteLeft": _note_for(pav_id, "left"),
                    "noteRight": _note_for(pav_id, "right"),
                })
            ptal_ids.append({
                "id": ptal.id,
                "attribute_id": ptal.attribute_id.id,
                "name": ptal.attribute_id.display_name,
                "display_type": ptal.attribute_id.display_type or "radio",
                "ptav_ids": values_payload,
            })
        return {"ptal_ids": ptal_ids}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("attribute_set_id") and vals.get("categ_id"):
                categ = self.env["product.category"].browse(vals["categ_id"])
                vals["attribute_set_id"] = categ.attribute_set_id.id
        return super().create(vals_list)

    def write(self, vals):
        # Keep template set in sync with category if set is missing
        if not vals.get("attribute_set_id") and vals.get("categ_id"):
            categ = self.env["product.category"].browse(vals["categ_id"])
            vals["attribute_set_id"] = categ.attribute_set_id.id
        return super().write(vals)






