# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict
from odoo import _, models, fields, api, exceptions
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    cpq_rules_product = fields.One2many("cpq.rules.product", "partner_id", string="Product Preferences")
    cpq_rules_order_note = fields.One2many("cpq.rules.order.note", "partner_id", string="Order Instructions")
    cpq_rules_logic = fields.One2many("cpq.rules.logic", "partner_id", string="Logic Rules")
    cpq_rules_nonproduct = fields.One2many("cpq.rules.nonproduct", "partner_id", string="Global Instructions")

    # picking_note = fields.Html(
    #     string="Picking Internal Note",
    #     help="The notes will be added to the sales order and"
    #     "pickings but will not be printed "
    #     "on the delivery slip.",
    # )
    # picking_customer_note = fields.Text(
    #     string="Picking Customer Comments",
    #     help="The notes will be added to the sales order and"
    #     "pickings and will be printed on "
    #     "the delivery slip.",
    # )
    
    inherited_cpq_rules_product = fields.One2many(
        "cpq.rules.product",
        compute="_compute_inherited_cpq_rules_product",
        string="Inherited Product Preferences",
        store=False,
    )

    @api.depends("parent_id")
    def _compute_inherited_cpq_rules_product(self):
        Rule = self.env["cpq.rules.product"]
        for partner in self:
            # Compute all ancestors except self
            ancestor_ids = partner.commercial_partner_id.ids if partner.commercial_partner_id else []
            _logger.info("Partner %s inherited from: %s", partner.id, ancestor_ids)

            if partner.id in ancestor_ids:
                ancestor_ids.remove(partner.id)

            if not ancestor_ids:
                partner.inherited_cpq_rules_product = Rule.browse()
                continue

            inherited = Rule.search([
                ("scope", "=", "global"),
                ("partner_id", "in", ancestor_ids),
                ("active", "=", True),
            ])
            partner.inherited_cpq_rules_product = inherited

# class ResPartner(models.Model):
#     _inherit = "res.partner"

#     preferences_count = fields.Integer(
#         compute="_compute_preferences_count", string="# Wishlists"
#     )

#     def _compute_preferences_count(self):
#         data = self.env["cpq.preferences.resolver"].read_group(
#             self._preference_domain(), ["partner_id"], ["partner_id"]
#         )
#         data_mapped = {
#             count["partner_id"][0]: count["partner_id_count"] for count in data
#         }
#         for rec in self:
#             rec.preferences_count = data_mapped.get(rec.id, 0)

#     def _preference_domain(self):
#         return [("partner_id", "in", self.ids), ("typology", "=", "preference")]

#     def action_view_preferences(self):
#         self.ensure_one()
#         xmlid = "product_set.act_open_product_set_view"
#         action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
#         action.update(
#             {
#                 "name": self.env._("Wishlists"),
#                 "domain": self._preference_domain(),
#                 "context": {
#                     "default_typology": "preference",
#                     "default_partner_id": self.id,
#                 },
#             }
#         )
#         return action
