from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductConfigPreference(models.Model):
    _name = "product.config.preference"
    _description = "Configurator Preference Rule"
    _order = "priority, id"
    
    # tip: add a SQL unique to prevent dupes
    _sql_constraints = [
      ("uniq_pref", "unique(partner_id, product_tmpl_id, attribute_id, pav_id, scope)",
       "This preference already exists.")
    ]

    active = fields.Boolean(default=True)
    partner_id = fields.Many2one("res.partner", required=True, index=True, help="Commercial partner; child contacts inherit.")
    product_tmpl_id = fields.Many2one("product.template", index=True, help="Optional: limit to a template.")
    attribute_id = fields.Many2one("product.attribute", required=True, index=True)
    allowed_attribute_ids = fields.Many2many(
        'product.attribute', compute='_compute_allowed_attrs', store=False
    )

    pav_id = fields.Many2one("product.attribute.value", required=True,
                             domain="[('attribute_id','=',attribute_id)]",
                             string="Preferred Value")
    scope = fields.Selection(
        [("shared", "Bilateral"), ("left", "Left"), ("right", "Right")],
        default="shared", required=True
    )
    priority = fields.Integer(default=10)
    note = fields.Char()

    # Clear caches when rules change (see section 3)
    def _invalidate_pref_cache(self):
        ProductT = self.env['product.template']
        # only if the method is cached will this exist
        if hasattr(ProductT._get_preference_payload, 'clear_cache'):
            ProductT._get_preference_payload.clear_cache(ProductT)
            
    def write(self, vals):
        res = super().write(vals)
        self._invalidate_pref_cache()
        return res

    def create(self, vals):
        rec = super().create(vals)
        rec._invalidate_pref_cache()
        return rec

    def unlink(self):
        res = super().unlink()
        self._invalidate_pref_cache()
        return res
    

    @api.depends(
        'product_tmpl_id',
        'product_tmpl_id.attribute_line_ids',
        'product_tmpl_id.attribute_line_ids.attribute_id',
    )
    def _compute_allowed_attrs(self):
        for rec in self:
            rec.allowed_attribute_ids = rec.product_tmpl_id.attribute_line_ids.mapped('attribute_id')
    
    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        self.ensure_one()
        self.attribute_id = False
        self.pav_id = False
        if self.product_tmpl_id:
            attr_ids = self.product_tmpl_id.attribute_line_ids.attribute_id.ids
            return {'domain': {'attribute_id': [('id', 'in', attr_ids)]}}
        return {'domain': {'attribute_id': []}}


    @api.model
    def toggle_preference(
        self,
        partner_id,
        product_tmpl_id,
        attribute_id,
        pav_id=None,
        ptav_id=None,
        scope="shared",
        preferred=True,
    ):
        self = self.sudo()

        partner = self.env["res.partner"].browse(partner_id).commercial_partner_id
        if not partner or not partner.exists():
            raise ValidationError(_("Invalid partner."))

        # Resolve PAV from PTAV if needed
        if not pav_id and ptav_id:
            ptav = self.env["product.template.attribute.value"].sudo().browse(ptav_id)
            if not ptav.exists():
                raise ValidationError(_("Invalid attribute value (PTAV)."))
            pav_id = ptav.product_attribute_value_id.id

        if not pav_id:
            raise ValidationError(_("Missing product attribute value (PAV)."))

        pav = self.env["product.attribute.value"].browse(pav_id)
        if not pav.exists():
            raise ValidationError(_("Invalid product attribute value (PAV)."))

        # Attribute/PAV consistency
        try:
            attribute_id = int(attribute_id)
        except Exception:
            raise ValidationError(_("Invalid attribute id."))

        if pav.attribute_id.id != attribute_id:
            raise ValidationError(_("Attribute/value mismatch."))

        # Normalize scope
        scope = scope if scope in ("left", "right", "shared") else "shared"

        # IMPORTANT: exact partner here (no child_of) to avoid clobbering parent/child rules
        dom = [
            ("partner_id", "=", partner.id),
            ("product_tmpl_id", "in", [False, product_tmpl_id]),
            ("attribute_id", "=", attribute_id),
            ("pav_id", "=", pav_id),
            ("scope", "=", scope),
        ]
        rule = self.search(dom, limit=1)

        if preferred:
            if rule:
                if not rule.active:
                    rule.write({"active": True})
                return {"id": rule.id, "preferred": True}
            vals = {
                "partner_id": partner.id,
                "product_tmpl_id": product_tmpl_id or False,
                "attribute_id": attribute_id,
                "pav_id": pav_id,
                "scope": scope,
                "priority": 10,
                "active": True,
            }
            rule = self.create(vals)
            return {"id": rule.id, "preferred": True}
        else:
            if rule:
                # keep audit trail; change to unlink() if you truly want hard delete
                rule.write({"active": False})
                return {"id": rule.id, "preferred": False}
            return {"id": False, "preferred": False}