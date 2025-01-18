import logging
import re
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    # Direct Affiliates
    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[("active", "=", True), ("is_company", "=", True)],
    )

    # Sub-Affiliates
    sub_affiliate_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Affiliates",
        compute="_compute_sub_affiliate_ids",
        store=False,
    )

    def _get_all_sub_affiliates(self):
        """
        Recursively fetch all sub-affiliates for the current partner, excluding direct affiliates.
        """
        sub_affiliates = self.env["res.partner"]
        for affiliate in self.affiliate_ids:
            sub_affiliates |= affiliate.affiliate_ids  # Direct affiliates of the current affiliate
            sub_affiliates |= affiliate._get_all_sub_affiliates()  # Recursively fetch deeper levels
        return sub_affiliates

    @api.depends("affiliate_ids", "affiliate_ids.affiliate_ids")
    def _compute_sub_affiliate_ids(self):
        """
        Compute sub-affiliates for each partner.
        """
        for partner in self:
            all_sub_affiliates = partner._get_all_sub_affiliates()
            partner.sub_affiliate_ids = all_sub_affiliates - partner.affiliate_ids  # Exclude direct affiliates


    is_contact = fields.Boolean(string="Contact", default=False)

    # child_ids = fields.One2many(
    #     "res.partner",
    #     compute="_compute_contacts",
    #     string="Contacts",
    #     index=True,
    # )

    child_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Contacts",
        domain=[("active", "=", True), ("is_company", "=", False)],
    )


    # @api.depends("parent_id", "is_company", "is_contact", "active")
    # def _compute_contacts(self):
    #     for record in self:
    #         if not isinstance(record.id, models.NewId):
    #             all_contacts = self.env["res.partner"].search(
    #                 [
    #                     ("id", "child_of", record.id),
    #                     ("is_company", "=", False),
    #                     ("is_contact", "=", True),
    #                     ("active", "=", True),
    #                 ]
    #             )
    #             record.child_ids = all_contacts
    #         else:
    #             record.child_ids = self.env["res.partner"]

    
    sub_contact_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Contacts",
        compute="_compute_sub_contact_ids",
        store=False,
    )

    def _get_all_sub_contacts(self):
        _logger.info(f"Fetching sub-contacts for: {self.name}")
        all_contacts = self.env["res.partner"]
        for contact in self.child_ids:
            all_contacts |= contact
            all_contacts |= contact._get_all_sub_contacts()
        _logger.info(f"Sub-contacts for {self.name}: {all_contacts}")
        return all_contacts

    @api.depends("child_ids", "child_ids.child_ids")
    def _compute_sub_contact_ids(self):
        """
        Compute all sub-contacts for each partner, excluding direct contacts.
        """
        for partner in self:
            all_sub_contacts = self.env["res.partner"]
            for child in partner.child_ids:
                # Add all descendants (recursive traversal)
                all_sub_contacts |= child._get_all_sub_contacts()
            # Assign only sub-contacts (exclude direct children)
            partner.sub_contact_ids = all_sub_contacts - partner.child_ids

    hide_parent = fields.Boolean(
        default=True,
        help="If selected, the parent's name will not be included in the "
        "display name of self.",
    )

    def _get_contact_name(self, partner, name):
        if partner.hide_parent:
            return name
        return super()._get_contact_name(partner, name)

    # Just add "hide_parent" as a trigger.
    @api.depends(
        "is_company", "name", "parent_id.name", "type", "company_name", "hide_parent"
    )
    def _compute_display_name(self):
        return super(ResPartner, self)._compute_display_name()


