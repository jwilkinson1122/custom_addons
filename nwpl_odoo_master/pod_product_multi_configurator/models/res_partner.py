# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict
from odoo import _, models, fields, api, exceptions
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    # Inline list on the partner form
    config_preference_ids = fields.One2many(
        "product.config.preference",
        "partner_id",
        string="Configurator Preferences",
        help="Preferences stored on this account (usually the commercial partner).",
    )

    config_pref_count = fields.Integer(compute="_compute_config_pref_count")

    def _compute_config_pref_count(self):
        Rule = self.env["product.config.preference"].sudo()
        for p in self:
            root = p.commercial_partner_id
            p.config_pref_count = Rule.search_count([("partner_id","child_of",root.id), ("active","=",True)])

    def action_open_config_preferences(self):
        self.ensure_one()
        root = self.commercial_partner_id
        return {
            "type": "ir.actions.act_window",
            "name": "Configurator Preferences",
            "res_model": "product.config.preference",
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("partner_id", "child_of", root.id)],
            "context": {"default_partner_id": root.id},
        }