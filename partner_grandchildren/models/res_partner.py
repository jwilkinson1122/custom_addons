from odoo import api, fields, models

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

    # Direct Contacts
    child_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Contacts",
        domain=[("active", "=", True), ("is_company", "=", False)],
    )

    # Sub-Contacts
    sub_contact_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Contacts",
        compute="_compute_sub_contact_ids",
        store=False,
    )

    def _get_all_sub_contacts(self):
        """
        Recursively fetch all sub-contacts for the current partner, excluding direct contacts.
        """
        sub_contacts = self.env["res.partner"]
        for contact in self.child_ids:
            sub_contacts |= contact.child_ids  # Direct children of the current contact
            sub_contacts |= contact._get_all_sub_contacts()  # Recursively fetch deeper levels
        return sub_contacts

    @api.depends("child_ids", "child_ids.child_ids")
    def _compute_sub_contact_ids(self):
        """
        Compute sub-contacts for each partner.
        """
        for partner in self:
            all_sub_contacts = partner._get_all_sub_contacts()
            partner.sub_contact_ids = all_sub_contacts - partner.child_ids  # Exclude direct contacts

