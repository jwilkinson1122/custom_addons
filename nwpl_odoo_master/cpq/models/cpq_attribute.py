import logging
from markupsafe import escape
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ..hooks import repair_cpq_attribute_links, cleanup_broken_cpq_values, fix_cpq_links, bulk_fix_is_custom_flags
from ..helpers.cpq_custom_field_utils import CPQCustomFieldMixin

_logger = logging.getLogger(__name__)

class CpqAttribute(models.Model):
    _inherit = ['avatar.mixin']
    _name = "cpq.attribute"
    _description = "Custom Attribute"
    _order = "sequence, name"
    _parent_name = "parent_id"
    _parent_store = True

    parent_path = fields.Char(index=True, unaccent=False)
    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(translate=True)
    display_type = fields.Selection([
        ("radio", "Radio Buttons"),
        ("select", "Dropdown"),
        ("color", "Color Swatch"),
        ("boolean", "Checkbox"),
        ("text", "Free Text"),
        ("number", "Number"),
        ("custom", "Custom"),
    ], default="radio", required=True)
    
    required = fields.Boolean(default=False)
    active = fields.Boolean(default=True)
    code = fields.Char("Internal Code")
    html_color = fields.Char("Color Code", help="Hex or HTML color code (for swatch display)")
    image_128 = fields.Image("Image 128", max_width=128, max_height=128)

    parent_id = fields.Many2one(
        'cpq.attribute',
        string='Parent Attribute',
        index=True,
        ondelete='cascade'   
    )

    child_ids = fields.One2many('cpq.attribute', 'parent_id', string="Child Records")

    subgroup_ids = fields.One2many(
        'cpq.attribute',
        'parent_id',
        string="Sub-Groups",
        domain=[('is_group', '=', True)]
    )

    subattribute_ids = fields.One2many(
        'cpq.attribute',
        'parent_id',
        string="Sub-Attributes",
        domain=[('is_group', '=', False)]
    )

    linked_product_attribute_id = fields.Many2one(
        "product.attribute",
        string="Linked Product Attribute",
        help="Used for bridging Custom attribute to product.attribute when generating virtual PTAVs."
    )
    
    child_badge_info = fields.Char(
        string="Child Badges",
        compute="_compute_child_badge_info",
        store=False
    )
    sub_attribute_count = fields.Integer("Sub-Attribute Count", compute='_compute_sub_attribute_count')
    value_ids = fields.One2many("cpq.attribute.value", "attribute_id", string="Values")
    note = fields.Text(string='Internal Note')
    is_group = fields.Boolean(string="Group", default=False) 
    group_label = fields.Char(
        string="Group Label",
        compute="_compute_group_label",
        store=True
    )
    
    @api.depends("is_group")
    def _compute_group_label(self):
        for rec in self:
            rec.group_label = "Group" if rec.is_group else "Attribute"
    
    group_order = fields.Integer(
        compute="_compute_group_order",
        store=True
    )

    @api.depends("is_group")
    def _compute_group_order(self):
        for rec in self:
            rec.group_order = 0 if rec.is_group else 1
    
    @api.depends("child_ids.name", "child_ids.is_group")
    def _compute_child_badge_info(self):
        for rec in self:
            names = [
                f"{child.name} (Group)" if child.is_group else child.name
                for child in rec.child_ids[:10] if child.name
            ]
            rec.child_badge_info = ", ".join(names)

    @api.depends('child_ids')
    def _compute_sub_attribute_count(self):
        for attribute in self:
            attribute.sub_attribute_count = len(attribute.child_ids)

    def _get_all_sub_attributes(self):
        return self.browse(set.union(set(), *self._get_sub_attribute_ids_per_attribute_id().values()))

    def _get_sub_attribute_ids_per_attribute_id(self):
        if not self:
            return {}

        res = dict.fromkeys(self._ids, [])
        if all(self._ids):
            self.env.cr.execute(
                """
         WITH RECURSIVE attribute_tree
                     AS (
                     SELECT id, id as superattribute_id
                       FROM cpq_attribute
                      WHERE id IN %(ancestor_ids)s
                      UNION
                         SELECT t.id, tree.superattribute_id
                           FROM cpq_attribute t
                           JOIN attribute_tree tree
                             ON tree.id = t.parent_id
                            AND t.active in (TRUE, %(active)s)
                          WHERE t.parent_id IS NOT NULL
               ) SELECT superattribute_id, ARRAY_AGG(id)
                   FROM attribute_tree
                  WHERE id != superattribute_id
               GROUP BY superattribute_id
                """,
                {
                    "ancestor_ids": tuple(self.ids),
                    "active": self._context.get('active_test', True),
                }
            )
            res.update(dict(self.env.cr.fetchall()))
        else:
            res.update({
                attribute.id: attribute._get_sub_attributes_recursively().ids
                for attribute in self
            })
        return res

    def _get_sub_attributes_recursively(self):
        children = self.child_ids
        if not children:
            return self.env['cpq.attribute']
        return children + children._get_sub_attributes_recursively()

    def action_open_parent_attribute(self):
        return {
            'name': _('Parent Attribute'),
            'view_mode': 'form',
            'res_model': 'cpq.attribute',
            'res_id': self.parent_id.id,
            'type': 'ir.actions.act_window',
            'context': self._context
        }

    def action_repair_cpq_links(self):
        result = repair_cpq_attribute_links(self.env)
        # Log or return result as needed
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Custom Repair Complete',
                'message': f"{len(result['values_created'])} values created, {len(result['values_skipped_existing'])} skipped.",
                'sticky': False,
            },
        }
   
    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._ensure_linked_product_attribute()
        return recs

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec._ensure_linked_product_attribute()  # keep the link/current name in sync
        return res

    def unlink(self):
        # see §4 for delete policy
        return super().unlink()

    def _ensure_linked_product_attribute(self):
        self.ensure_one()
        if self.env.context.get("cpq_sync_silent"):
            return
        ProductAttr = self.env["product.attribute"].sudo().with_company(self.env.company)
        pa = self.linked_product_attribute_id
        if pa:
            try:
                pa.write({"name": self.name})
            except Exception:
                pass
            return pa
        pa = ProductAttr.search([("name", "=", self.name)], limit=1)
        if not pa:
            pa = ProductAttr.create({
                "name": self.name,
                "create_variant": "no_variant",  # keep CPQ friendly
            })
        self.with_context(cpq_sync_silent=True).write({
            "linked_product_attribute_id": pa.id
        })
        return pa

class CpqAttributeValue(models.Model, CPQCustomFieldMixin):
    _name = "cpq.attribute.value"
    _description = "Custom Attribute Value"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    price_extra = fields.Float("Extra Price")
    description = fields.Text(translate=True)
    attribute_id = fields.Many2one("cpq.attribute", required=True, ondelete="cascade")

    child_attribute_id = fields.Many2one(
        "cpq.attribute",
        string="Sub-Attribute",
        help="Selecting this value will trigger this sub-attribute to be displayed."
    )

    triggers_child_attribute_ids = fields.Many2many(
        'cpq.attribute',
        'cpq_attribute_value_child_rel',
        'value_id', 'attribute_id',
        string='Triggers Attributes'
    )

    active = fields.Boolean(default=True)
    code = fields.Char("Internal Code")
    html_color = fields.Char("Color Code", help="Hex or HTML color code (for swatch display)")
    is_custom = fields.Boolean("Allow Free Input")
    image_128 = fields.Image("Image", max_width=128, max_height=128)
    cpq_custom_type = fields.Selection([
        ("integer", "Integer"),
        ("float", "Float"),
        ("char", "Text"),
        ("many2one", "Many2one"),
        ("options", "Option"),
    ], string="Custom Input Type")

    linked_product_id = fields.Many2one("product.template", string="Linked Component")

    linked_option_id = fields.Many2one(
        "product.options",
        string="Linked Option",
        domain="[('is_leaf', '=', True)]",
        # ondelete='cascade',
        help="Select a predefined product option this attribute value should be associated with. "
         "Used to map free-form or selectable values to structured configuration options under "
         "Custom Options (e.g., 'Heel Options', 'Top Cover Options')."
    )

    linked_attribute_id = fields.Many2one(
        related="linked_option_id.option_id",
        string="Linked Attribute",
        store=True,
        readonly=True
    )
    
    linked_product_attribute_value_id = fields.Many2one(
        'product.attribute.value', ondelete='set null'
    )

    cpq_options_relaxed_validation = fields.Boolean(
        string="Relax Validation",
        help="Allow a options record to be moved between parents",
        default=False,
    )

    computed_product_attribute_id = fields.Many2one(
        "product.attribute",
        string="Computed Product Attribute",
        compute="_compute_product_attribute",
        store=False,
    )

    @api.depends("attribute_id.linked_product_attribute_id")
    def _compute_product_attribute(self):
        for val in self:
            val.computed_product_attribute_id = val.attribute_id.linked_product_attribute_id

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._ensure_linked_pav()  
        return recs

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec._ensure_linked_pav(update_name=True)
        return res
    
    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if "name" not in default:
            default["name"] = _("%s (copy)") % (self.name)
        return super().copy(default=default)
    
    def unlink(self):
        for rec in self:
            pav = rec.linked_product_attribute_value_id
            super(CpqAttributeValue, rec).unlink()
            if pav:
                refs = self.env["product.template.attribute.value"].sudo().search_count([
                    ("product_attribute_value_id", "=", pav.id)
                ])
                if refs == 0:
                    try:
                        pav.unlink()
                    except Exception:
                        pav.write({"active": False})
        return True

    def _ensure_linked_pav(self, *, update_name=False):
        self.ensure_one()
        if self.env.context.get("cpq_sync_silent"):
            return
        pattr = self.attribute_id._ensure_linked_product_attribute()
        PAV = self.env["product.attribute.value"].sudo().with_company(self.env.company)
        pav = self.linked_product_attribute_value_id

        if not pav:
            pav = PAV.search([
                ("attribute_id", "=", pattr.id),
                ("name", "=", self.name),
            ], limit=1)
        if not pav:
            pav = PAV.create({"attribute_id": pattr.id, "name": self.name})
        elif update_name and pav.name != self.name:
            try:
                pav.write({"name": self.name})
            except Exception:
                pass

        # ✅ copy CPQ image onto the PAV if the PAV supports images and is empty
        try:
            if "image_1920" in PAV._fields:
                src = self.image_128 or False
                if src and not pav.image_1920:
                    # write the CPQ image into the PAV large slot; Odoo will derive 128px automatically
                    pav.write({"image_1920": src})
        except Exception:
            # never let image sync break linking
            pass

        self.with_context(cpq_sync_silent=True).write({"linked_product_attribute_value_id": pav.id})
        return pav

    @api.model
    def _cron_backfill_links(self, limit=500):
        """Backfill/repair CPQ ↔ Product links and push images where missing."""
        attrs = self.env["cpq.attribute"].search(
            [("linked_product_attribute_id", "=", False)], limit=limit
        )
        for a in attrs:
            a._ensure_linked_product_attribute()

        vals_missing = self.search([("linked_product_attribute_value_id", "=", False)], limit=limit)
        for v in vals_missing:
            v._ensure_linked_pav()

        vals_linked = self.search([("linked_product_attribute_value_id", "!=", False)])
        for v in vals_linked:
            v._ensure_linked_pav(update_name=True)

    def cleanup_cpq_values_ui(self):
        env = self.env
        broken_ids = cleanup_broken_cpq_values(env, auto_delete=True)
        raise UserError(" Cleanup complete.\nDeleted %s broken Custom value(s)." % len(broken_ids))
    
    @api.model
    def fix_links_ui(self):
        fix_cpq_links(self.env)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Custom Repair",
                "message": "Link repair completed successfully.",
                "type": "success",
                "sticky": False,
            },
        }

class CpqAttributeChildLink(models.Model):
    _name = "cpq.attribute.child.link"
    _description = "Custom Attribute Child Link"

    parent_value_id = fields.Many2one("cpq.attribute.value", required=True, ondelete="cascade")
    child_attribute_id = fields.Many2one("cpq.attribute", required=True, ondelete="cascade")
