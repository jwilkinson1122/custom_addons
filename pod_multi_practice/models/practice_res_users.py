# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import exceptions
from odoo.exceptions import UserError


class ResUsers(models.Model):
    """inherited res users"""

    _inherit = "res.users"

    # practice_ids = fields.Many2many(
    #     "res.practice",
    #     string="Allowed Practices",
    #     domain="[('company_id', '=', company_ids)]",
    # )

    practice_ids = fields.Many2many(
        "res.practice",
        string="Allowed Practices",
        # Removed 'company_id' restriction
    )

    practice_id = fields.Many2one(
        "res.practice",
        string="Default Practice",
        default=False,
        domain="[('id', '=', practice_ids)]",
    )

    @api.constrains("practice_id")
    def practice_constrains(self):
        """practice constrains"""
        company = self.env.company
        for user in self:
            if user.practice_id and user.practice_id.company_id != company:
                raise exceptions.UserError(
                    _(
                        "Sorry! The selected Practice does "
                        "not belong to the current Company"
                        " '%s'",
                        company.name,
                    )
                )

    def _get_default_warehouse_id(self):
        """method to get default warehouse id"""
        if self.property_warehouse_id:
            return self.property_warehouse_id
        # !!! Any change to the following search domain should probably
        # be also applied in sale_stock/models/sale_order.py/_init_column.
        if len(self.env.user.practice_ids) == 1:
            warehouse = self.env["stock.warehouse"].search(
                [("practice_id", "=", self.env.user.practice_id.id)], limit=1
            )
            if not warehouse:
                warehouse = self.env["stock.warehouse"].search(
                    [("practice_id", "=", False)], limit=1
                )
            if not warehouse:
                error_msg = _(
                    "No warehouse could be found in the '%s' practice",
                    self.env.user.practice_id.name,
                )
                raise UserError(error_msg)
            return warehouse
        else:
            return self.env["stock.warehouse"].search(
                [("company_id", "=", self.env.company.id)], limit=1
            )
