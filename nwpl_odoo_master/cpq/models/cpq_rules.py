# -*- coding: utf-8 -*-
import logging
import json
from odoo import api, fields, models
# from odoo.addons.pod_log.tools.db_logger import PodDBLogger 
from ...pod_log.tools.db_logger import PodDBLogger 
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class CpqAbstractRule(models.AbstractModel):
    _name = "cpq.rules.abstract"
    _description = "Abstract Base for CPQ Rules"
    _order = "partner_id, product_tmpl_id"

    scope = fields.Selection([
        ("global", "Global (inherited)"),
        ("partner", "Company/Account-specific"),
        ("user", "User-specific"),
        ("product", "Applies to all products"),
        ("product_specific", "Applies only to one product"),
    ], required=True)

    partner_id = fields.Many2one("res.partner", string="Customer/Account")
    contact_id = fields.Many2one("res.partner", string="Contact/User", domain="[('is_contact', '=', True)]")
    product_tmpl_id = fields.Many2one("product.template", string="Product")
    active = fields.Boolean(default=True)
    note = fields.Text("Instruction or Note")
    condition_json = fields.Text("Condition (JSON Logic)")
    
    @api.onchange("partner_id", "contact_id")
    def _onchange_scope_filter(self):
        """
        Dynamically constrain the available scope values depending on the context.
        This affects the selection domain via view customization (see note).
        """
        scopes = [("global", "Global (inherited to children)")]

        if self.partner_id and self.partner_id.is_account:
            scopes.append(("partner", "Company/Account-specific"))

        if self.contact_id and self.contact_id.is_contact:
            scopes.append(("user", "User-specific"))

        scopes += [
            ("product", "Applies to all products"),
            ("product_specific", "Applies only to one product")
        ]

        # ❗ NOTE: Dynamically changing selection options on a Selection field
        # is not natively supported without JS or a computed helper field.
        # So this just resets the value if it's invalid.
        valid_keys = [s[0] for s in scopes]
        if self.scope not in valid_keys:
            self.scope = False

        # Log or use with context-aware views if needed
        self._scope_domain_override = scopes  # for debugging/testing
 
# Product Configuration Preferences
class CpqRulesProduct(models.Model):
    _name = "cpq.rules.product"
    _description = "Product Preference Rule"
    _inherit = "cpq.rules.abstract"

    attribute_id = fields.Many2one("cpq.attribute", string="Attribute")
    value_id = fields.Many2one("cpq.attribute.value", string="Preferred Value")

    @api.onchange('partner_id', 'contact_id')
    def _onchange_scope_filter(self):
        is_account = self.partner_id and self.partner_id.is_account
        is_contact = self.contact_id and self.contact_id.is_contact

        options = [('global', 'Global (inherited to children)')]
        if is_account:
            options.append(('partner', 'Company/Account-specific'))
        if is_contact:
            options.append(('user', 'User-specific'))
        options.append(('product', 'Applies to all products'))
        options.append(('product_specific', 'Applies only to one product'))

        self.scope = False  # Reset scope to prevent invalid value
        return {'domain': {'scope': [('key', 'in', [opt[0] for opt in options])]}}

    _sql_constraints = [
        ("product_pref_unique",
         "unique(partner_id, contact_id, product_tmpl_id, attribute_id)",
         "Only one product attribute rule allowed per attribute.")
    ]

# Special Instructions On Orders
class CpqRulesOrderNote(models.Model):
    _name = "cpq.rules.order.note"
    _description = "Special Instruction Rule"
    _inherit = "cpq.rules.abstract"


class CpqRulesLogic(models.Model):
    _name = "cpq.rules.logic"
    _description = "Conditional Logic Rule"
    _inherit = "cpq.rules.abstract"

# General Non-Product Instructions
class CpqRulesNonProduct(models.Model):
    _name = "cpq.rules.nonproduct"
    _description = "Global Non-Product Instruction Rule"
    _inherit = "cpq.rules.abstract"


class CPQPreferencesResolver(models.AbstractModel):
    _name = "cpq.preferences.resolver"
    _description = "CPQ Preferences Rule Resolver"

    @api.model
    def resolve_preferences_payload(self, partner, user=None, product_tmpl=None):
        return {
            "product": self.resolve_preferences(partner, user=user, product_tmpl=product_tmpl),
            "order_notes": self.resolve_notes(partner, user=user),
            "nonproduct": [r.read(['note', 'scope', 'condition_json'])[0] for r in self.resolve_nonproduct_instructions(partner)],
            "logic": [r.read(['note', 'scope', 'condition_json'])[0] for r in self.resolve_logic_rules(partner)],
        }

    @api.model
    def resolve_preferences(self, partner, user=None, product_tmpl=None):
        _log = PodDBLogger(self.env.cr.dbname, 'res.partner', partner.id, self.env.uid)
        _log.info(f"[resolve_preferences] Matching rules for partner {partner.name} ({partner.id}) and user {user.name if user else 'N/A'}")

        preferences = {}
        detailed_preferences = []
        seen = set()
        ptav_model = self.env["product.template.attribute.value"]

        partner_domain = ['|',
            ('partner_id', 'child_of', partner.id),
            ('partner_id', 'child_of', partner.commercial_partner_id.id),
        ]

        user_domain = [('contact_id', '=', user.partner_id.id if user else False)]

        rules = self.env['cpq.rules.product'].search([
            ('active', '=', True),
            '|',
                '&', ('scope', 'in', ['global', 'partner']), *partner_domain,
                '&', ('scope', '=', 'user'), *user_domain,
            '|', ('product_tmpl_id', '=', False), ('product_tmpl_id', '=', product_tmpl.id if product_tmpl else False),
        ])

        _log.info(f"[resolve_preferences] Found {len(rules)} rules")

        # Log breakdown of domain component results
        base_model = self.env["cpq.rules.product"]

        partner_rules = base_model.search([('scope', 'in', ['partner']), ('active', '=', True), *partner_domain])
        _log.info(f"Partner-based rules found: {len(partner_rules)}")

        if user and user.partner_id:
            user_rules = base_model.search([('scope', '=', 'user'), ('active', '=', True), *user_domain])
            _log.info(f"User-based rules found: {len(user_rules)}")
        else:
            _log.warning("User or user.partner_id missing — skipping user-based rule test.")

        global_rules = base_model.search([('scope', '=', 'global'), ('active', '=', True)])
        _log.info(f"Global rules found: {len(global_rules)}")

        if product_tmpl:
            tmpl_rules = base_model.search([
                ('active', '=', True),
                '|', ('product_tmpl_id', '=', False), ('product_tmpl_id', '=', product_tmpl.id)
            ])
            _log.info(f"Template-linked rules (including generic): {len(tmpl_rules)}")
        else:
            _log.warning("No product_tmpl provided — skipping product_tmpl domain test.")

        if not rules:
            _log.warning("No preference rules matched for:")
            _log.warning(f"  Partner ID: {partner.id} (commercial_partner_id: {partner.commercial_partner_id.id})")
            _log.warning(f"  User: {user.name if user else 'N/A'} (user.partner_id: {user.partner_id.id if user else 'N/A'})")
            _log.warning(f"  Product Template ID: {product_tmpl.id if product_tmpl else 'N/A'}")

            all_rules = self.env["cpq.rules.product"].search([("active", "=", True)])
            scope_counts = {}
            for r in all_rules:
                scope_counts[r.scope] = scope_counts.get(r.scope, 0) + 1
            _log.info(f"[resolve_preferences] Total active rules by scope: {json.dumps(scope_counts)}")

            sample = all_rules[:5]
            for rule in sample:
                _log.info(f"Sample Rule → Scope: {rule.scope}, Partner: {rule.partner_id.id if rule.partner_id else '❌'}, "
                          f"User: {rule.contact_id.id if rule.contact_id else '❌'}, "
                          f"Template: {rule.product_tmpl_id.id if rule.product_tmpl_id else 'Any'}, "
                          f"Attr: {rule.attribute_id.name if rule.attribute_id else '❌'}, "
                          f"Value: {rule.value_id.name if rule.value_id else '❌'}")

        for rule in rules:
            if not (rule.attribute_id and rule.value_id and product_tmpl):
                continue

            key = (rule.attribute_id.id, rule.value_id.id)
            if key in seen:
                continue
            seen.add(key)

            ptav = ptav_model.search([
                ("x_virtual_cpq_id", "=", rule.value_id.id),
                ("attribute_id", "=", rule.attribute_id.id),
                ("product_tmpl_id", "=", product_tmpl.id),
            ], limit=1)

            _log.debug(f"[Rule] Attribute: {rule.attribute_id.name} | Value: {rule.value_id.name} | Scope: {rule.scope}")

            if not ptav:
                virtual_ptavs = product_tmpl._cpq_generate_virtual_ptavs(rule.value_id)
                product_attr = rule.attribute_id.linked_product_attribute_id
                ptav = virtual_ptavs.filtered(lambda pt: pt.attribute_id.id == product_attr.id if product_attr else False)
                _logger.info("[RESOLVE] Rule: Attr=%s, Val=%s (IDs: %s/%s), Scope=%s, Linked Product Attr=%s",
                             rule.attribute_id.name,
                             rule.value_id.name,
                             rule.attribute_id.id,
                             rule.value_id.id,
                             rule.scope,
                             rule.attribute_id.linked_product_attribute_id.id if rule.attribute_id.linked_product_attribute_id else "None")
                if ptav:
                    ptav = ptav[0]
                    _log.debug(f"Matched PTAV ID {ptav.id} for value {rule.value_id.name}")
                else:
                    _log.warning(f"Could not match PTAV for value {rule.value_id.name} on attribute {rule.attribute_id.name}")
                    ptav = False
            if ptav:
                preferred_key = str(ptav.x_virtual_cpq_id or ptav.id)
                preferences[preferred_key] = True
                detailed_preferences.append({
                    "attribute_id": rule.attribute_id.id,
                    "value_id": rule.value_id.id,
                    "ptav_id": ptav.id,
                    "ptav_name": ptav.name,
                    "attribute_name": ptav.attribute_id.name,
                    "scope": rule.scope,
                    "note": rule.note or "",
                })
                _log.debug(f"Mapped cpq.value {rule.value_id.display_name} → PTAV ID {ptav.id} ({ptav.display_name})")
            else:
                _log.warning(f"Could not generate PTAV for value {rule.value_id.name} on attribute {rule.attribute_id.name}")

        try:
            _log.info(f"[resolve_preferences] Final selected:\n{json.dumps(preferences, indent=2)}")
        except TypeError:
            _log.warning("[resolve_preferences] Skipping JSON log of preferences due to non-serializable objects")

        try:
            _log.info(f"[resolve_preferences] Detailed:\n{json.dumps(detailed_preferences, indent=2)}")
        except TypeError:
            _log.warning("[resolve_preferences] Skipping JSON log of detailed_preferences due to non-serializable objects")

        return {
            "selected": preferences,
            "detailed": detailed_preferences,
        }

    @api.model
    def resolve_notes(self, partner, user=None):
        rules = self.env['cpq.rules.order.note'].search([
            ('active', '=', True),
            '|', ('partner_id', 'child_of', partner.id), ('partner_id', '=', False),
            '|', ('contact_id', '=', user.id if user else False), ('contact_id', '=', False),
        ])
        return [rule.note for rule in rules if rule.note]

    @api.model
    def resolve_nonproduct_instructions(self, partner):
        return self.env['cpq.rules.nonproduct'].search([
            ('partner_id', 'child_of', partner.id),
            ('active', '=', True),
        ])

    @api.model
    def resolve_logic_rules(self, partner):
        return self.env['cpq.rules.logic'].search([
            ('partner_id', 'child_of', partner.id),
            ('active', '=', True),
        ])

# class ProductSet(models.Model):
#     _inherit = "product.set"

#     typology = fields.Selection(
#         selection=[("set", "Default"), ("wishlist", "Wishlist")], default="set"
#     )