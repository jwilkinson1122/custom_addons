# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BranchPartner(models.Model):
    """inherited partner"""

    _inherit = "res.partner"

    branch_id = fields.Many2one(
        "res.branch",
        string="Branch",
        store=True,
        help="Branch associated with this partner.",
        domain="[('id', 'in', affiliate_branch_ids)]",
    )

    affiliate_branch_ids = fields.Many2many(
        "res.branch",
        "branch_partner_rel",
        "partner_id",
        "branch_id",
        string="Afilliate Branches",
        compute="_compute_affiliate_branch_ids",
        help="Branches associated with the parent partner or allowed branches for this partner.",
    )

    is_multiple_branch = fields.Boolean(
        string="Multiple Branches", compute="_compute_is_multiple_branch"
    )

    # @api.depends("company_id")
    # def _compute_affiliate_branch_ids(self):
    #     for po in self:
    #         if po.is_multiple_company:
    #             if po.company_id:
    #                 branch_ids = []
    #                 for rec in po.env.user.branch_ids:
    #                     if rec.company_id == po.company_id:
    #                         branch_ids.append(rec.id)
    #                 po.affiliate_branch_ids = branch_ids
    #             else:
    #                 po.affiliate_branch_ids = po.env.user.branch_ids.ids
    #         else:
    #             po.affiliate_branch_ids = po.env.user.branch_ids.ids

    # @api.depends("company_id")
    # def _compute_is_multiple_company(self):
    #     """checking is this multi company or not"""
    #     for rec in self:
    #         rec.is_multiple_company = False
    #         company_count = self.env["res.company"].search_count([])
    #         if company_count > 1:
    #             rec.is_multiple_company = True

    @api.depends("parent_id")
    def _compute_affiliate_branch_ids(self):
        """Set the allowed branches based on the parent or user."""
        for partner in self:
            if partner.parent_id:
                partner.affiliate_branch_ids = partner.parent_id.branch_id
            else:
                partner.affiliate_branch_ids = self.env.user.branch_ids

    @api.depends("parent_id")
    def _compute_is_multiple_branch(self):
        """Check if the partner is associated with multiple branches."""
        for partner in self:
            partner.is_multiple_branch = len(partner.affiliate_branch_ids) > 1

    @api.model
    def default_get(self, default_fields):
        """Add the company of the parent as default if we are creating a
        child partner.Also take the parent lang by default if any, otherwise,
        fallback to default DB lang."""
        values = super().default_get(default_fields)
        parent = self.env["res.partner"]
        if "parent_id" in default_fields and values.get("parent_id"):
            parent = self.browse(values.get("parent_id"))
            values["branch_id"] = parent.branch_id.id
        return values

    # @api.onchange("parent_id", "branch_id")
    # def _onchange_parent_id(self):
    #     """methode to set branch on changing the parent company"""
    #     if self.parent_id:
    #         self.branch_id = self.parent_id.branch_id.id

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        """Set branch to match the parent when parent is selected."""
        if self.parent_id:
            self.branch_id = self.parent_id.branch_id

    # def write(self, vals):
    #     """override write methode"""
    #     if vals.get("branch_id"):
    #         branch_id = vals["branch_id"]
    #         for partner in self:
    #             for child in partner.child_ids:
    #                 child.write({"branch_id": branch_id})
    #     else:
    #         for partner in self:
    #             for child in partner.child_ids:
    #                 child.write({"branch_id": False})
    #     result = super(BranchPartner, self).write(vals)
    #     return result

    def write(self, vals):
        """Propagate branch changes to child partners."""
        if "branch_id" in vals:
            branch_id = vals["branch_id"]
            for partner in self:
                if partner.child_ids:
                    partner.child_ids.write({"branch_id": branch_id})
        return super().write(vals)
