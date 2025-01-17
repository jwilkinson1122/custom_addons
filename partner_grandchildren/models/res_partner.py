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


# class ResPartner(models.Model):
#     _inherit = "res.partner"

#     affiliate_ids = fields.One2many(
#         "res.partner",
#         "parent_id",
#         string="Affiliates",
#         domain=[("active", "=", True), ("is_company", "=", True)],
#     )

#     sub_affiliate_ids = fields.One2many(
#         comodel_name="res.partner",
#         string="Sub-Affiliates",
#         compute="_compute_sub_affiliate_ids",
#         store=False,
#     )

#     def _get_all_sub_affiliates(self):
#         """
#         Recursively fetch all sub-affiliates for the current partner.
#         """
#         all_affiliates = self.env["res.partner"]
#         for affiliate in self.affiliate_ids:
#             all_affiliates |= affiliate
#             all_affiliates |= affiliate._get_all_sub_affiliates()
#         return all_affiliates

#     @api.depends("affiliate_ids", "affiliate_ids.affiliate_ids")
#     def _compute_sub_affiliate_ids(self):
#         """
#         Compute all sub-affiliates for each partner.
#         """
#         for partner in self:
#             partner.sub_affiliate_ids = partner._get_all_sub_affiliates()

#     def _set_affiliate_company_type(self):
#         """
#         Ensure that affiliates always have the `company_type` set to 'company'.
#         """
#         for affiliate in self.affiliate_ids:
#             if affiliate.company_type != 'company':
#                 affiliate.company_type = 'company'

#     @api.model
#     def create(self, vals):
#         """
#         Override the create method to set company_type to 'company' for affiliates.
#         """
#         record = super(ResPartner, self).create(vals)
#         if vals.get("parent_id") and vals.get("is_company"):
#             record.company_type = "company"
#         return record

#     def write(self, vals):
#         """
#         Override the write method to ensure company_type is 'company' for affiliates.
#         """
#         res = super(ResPartner, self).write(vals)
#         if "affiliate_ids" in vals:
#             self._set_affiliate_company_type()
#         return res

#     child_ids = fields.One2many(
#         "res.partner",
#         "parent_id",
#         string="Contacts",
#         domain=[("active", "=", True), ("is_company", "=", False)],
#     )

#     sub_contact_ids = fields.One2many(
#         comodel_name="res.partner",
#         string="Sub-Contacts",
#         compute="_compute_sub_contact_ids",
#         store=False,
#     )

#     def _get_all_sub_contacts(self):
#         """
#         Recursively fetch all sub-contacts for the current partner.
#         """
#         all_contacts = self.env["res.partner"]
#         for contact in self.child_ids:
#             all_contacts |= contact
#             all_contacts |= contact._get_all_sub_contacts()
#         return all_contacts

#     @api.depends("child_ids", "child_ids.child_ids")
#     def _compute_sub_contact_ids(self):
#         """
#         Compute all sub-contacts for each partner.
#         """
#         for partner in self:
#             partner.sub_contact_ids = partner._get_all_sub_contacts()

#     def open_partner_form(self):
#             """Open form from the parent partner form view"""
#             return {
#                 "type": "ir.actions.act_window",
#                 "res_model": "res.partner",
#                 "res_id": self.id,
#                 "view_mode": "form",
#                 "target": "current",
#             }
    