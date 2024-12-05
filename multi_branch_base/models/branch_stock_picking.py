# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    """inherited stock.picking"""

    _inherit = "stock.picking"

    def _get_default_branch_id(self):
        if len(self.env.user.branch_ids) == 1:
            sp_company = self.company_id if self.company_id else self.env.company
            branch_ids = self.env.user.branch_ids
            branch = branch_ids.filtered(lambda branch: branch.company_id == sp_company)
            if branch:
                return branch
            else:
                return False
        return False

    branch_id = fields.Many2one(
        "res.branch",
        string="Branch",
        readonly=False,
        store=True,
        compute="_compute_branch_id",
        default=_get_default_branch_id,
    )

    @api.depends("sale_id", "purchase_id")
    def _compute_branch_id(self):
        """methode to compute branch"""
        for record in self:
            record.branch_id = False
            if record.sale_id.branch_id:
                record.branch_id = record.sale_id.branch_id
            if record.purchase_id.branch_id:
                record.branch_id = record.purchase_id.branch_id


class StockPickingTypes(models.Model):
    """inherited stock picking type"""

    _inherit = "stock.picking.type"

    branch_id = fields.Many2one(
        "res.branch", string="Branch", store=True, related="warehouse_id.branch_id"
    )
