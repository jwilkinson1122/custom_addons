import logging
from markupsafe import escape
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ..hooks import repair_cpq_attribute_links, cleanup_broken_cpq_values, fix_cpq_links, bulk_fix_is_custom_flags
from ..helpers.cpq_custom_field_utils import CPQCustomFieldMixin

_logger = logging.getLogger(__name__)

class CpqAttribute(models.Model):
    _name = "cpq.attribute"
    _description = "CPQ Attribute"
    _order = "sequence, name"
    _parent_name = "parent_id"
    _parent_store = True

    parent_path = fields.Char(index=True)

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

    # parent_id = fields.Many2one("cpq.attribute", string="Parent Attribute", index=True, ondelete='cascade')
    # child_ids = fields.One2many("cpq.attribute", "parent_id", string="Sub-Attributes")
    parent_id = fields.Many2one(
        'cpq.attribute',
        string='Parent Attribute',
        index=True,
        ondelete='cascade'   
    )

    # parent_id = fields.Many2one('cpq.attribute', string='Parent Attribute', index=True, domain="['!', ('id', 'child_of', id)]", tracking=True)
    child_ids = fields.One2many('cpq.attribute', 'parent_id', string="Sub-attributes")
    # child_badge_info = fields.Json("Child Badges", compute="_compute_child_badge_info", store=False)
    linked_product_attribute_id = fields.Many2one(
        "product.attribute",
        string="Linked Product Attribute",
        help="Used for bridging CPQ attribute to product.attribute when generating virtual PTAVs."
    )
    child_badge_info = fields.Char(
        string="Child Badges",
        compute="_compute_child_badge_info",
        store=False
    )
    sub_attribute_count = fields.Integer("Sub-Attribute Count", compute='_compute_sub_attribute_count')
    value_ids = fields.One2many("cpq.attribute.value", "attribute_id", string="Values")
    is_group = fields.Boolean(string="Is Group", default=False) 
    note = fields.Text(string='Internal Note')

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
                'title': 'CPQ Repair Complete',
                'message': f"{len(result['values_created'])} values created, {len(result['values_skipped_existing'])} skipped.",
                'sticky': False,
            },
        }
   
class CpqAttributeValue(models.Model, CPQCustomFieldMixin):
    _name = "cpq.attribute.value"
    _description = "CPQ Attribute Value"
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
    
    cpq_custom_type = fields.Selection([
        ("integer", "Integer"),
        ("float", "Float"),
        ("char", "Text"),
        ("many2one", "Many2one"),
        ("options", "Option"),
    ], string="Custom Input Type")

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

    cpq_options_relaxed_validation = fields.Boolean(
        string="Relax Validation",
        help="Allow a options record to be moved between parents",
        default=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._ensure_option_links()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._ensure_option_links()
        return res

    def _ensure_option_links(self):
        """
        Ensures that each linked_option_id has a valid option_id set based on the value's attribute.
        """
        for val in self:
            option = val.linked_option_id
            cpq_attr = val.attribute_id
            product_attr = cpq_attr.linked_product_attribute_id

            if option and not option.option_id and product_attr:
                option.option_id = product_attr
                _logger.info("🔗 [Auto-link] Set option_id=%s on product.options '%s' from cpq.attribute '%s'",
                             product_attr.name, option.name, cpq_attr.name)


    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if "name" not in default:
            default["name"] = _("%s (copy)") % (self.name)
        return super().copy(default=default)
    
    def cleanup_cpq_values_ui(self):
        env = self.env
        broken_ids = cleanup_broken_cpq_values(env, auto_delete=True)
        raise UserError(" Cleanup complete.\nDeleted %s broken CPQ value(s)." % len(broken_ids))
    
    @api.model
    def fix_links_ui(self):
        fix_cpq_links(self.env)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "CPQ Repair",
                "message": "Link repair completed successfully.",
                "type": "success",
                "sticky": False,
            },
        }

class CpqAttributeChildLink(models.Model):
    _name = "cpq.attribute.child.link"
    _description = "CPQ Attribute Child Link"

    parent_value_id = fields.Many2one("cpq.attribute.value", required=True, ondelete="cascade")
    child_attribute_id = fields.Many2one("cpq.attribute", required=True, ondelete="cascade")
