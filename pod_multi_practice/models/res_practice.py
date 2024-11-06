# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class Practice(models.Model):
    _name = "res.practice"
    _description = "Company Practices"
    _order = "name"

    active = fields.Boolean(default=True)
    name = fields.Char(string="Practice", required=True, store=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        store=True,
        domain="[('is_practice_partner', '=', True)]",  # Filter to show only practice partners
    )
    parent_practice_id = fields.Many2one(
        "res.practice",
        string="Parent Practice",
        help="The parent practice of this practice, if any.",
        store=True,
    )
    child_practice_ids = fields.One2many(
        "res.practice",
        "parent_practice_id",
        string="Child Practices",
        help="Practices under this practice.",
    )

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one(
        "res.country.state",
        string="Fed. State",
        domain="[('country_id', '=?', country_id)]",
    )
    country_id = fields.Many2one("res.country", string="Country")
    email = fields.Char(store=True)
    phone = fields.Char(store=True)
    website = fields.Char()

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The Practice name must be unique!")
    ]

    @api.model
    def create(self, vals):
        # Automatically create a partner associated with this practice
        partner_vals = {
            "name": vals.get("name"),
            "is_practice_partner": True,
            "is_company": True,  # Ensures it shows as a company in Contacts
        }
        partner = self.env["res.partner"].create(partner_vals)
        vals["partner_id"] = partner.id  # Link the created partner to this practice
        return super(Practice, self).create(vals)
