# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    create_rma = fields.Boolean(string="Create RMAs")
    picking_type_code = fields.Selection(related="picking_id.picking_type_id.code")
    rma_location_ids = fields.Many2many(
        comodel_name="stock.location", compute="_compute_rma_location_id"
    )
    # Expand domain for RMAs
    location_id = fields.Many2one(
        domain="create_rma and [('id', 'child_of', rma_location_ids)]"
        "or "
        "['|', ('id', '=', original_location_id), '|', '&', "
        "('return_location', '=', True), ('company_id', '=', False), '&', "
        "('return_location', '=', True), ('company_id', '=', company_id)]"
    )

    @api.depends("picking_id")
    def _compute_rma_location_id(self):
        for record in self:
            record.rma_location_ids = (
                self.env["stock.warehouse"]
                .search([("company_id", "=", record.picking_id.company_id.id)])
                .rma_loc_id
            )

    @api.onchange("create_rma")
    def _onchange_create_rma(self):
        if self.create_rma:
            warehouse = self.picking_id.picking_type_id.pod_warehouse_id
            self.location_id = warehouse.rma_loc_id.id
            # We want to avoid setting the return move `to_refund` as it will change
            # the delivered quantities in the sale and set them to invoice.
            self.product_return_moves.to_refund = False
        else:
            # If self.create_rma is not True, the value of the location will be the
            # same as assigned by default
            location_id = self.picking_id.location_id.id
            return_picking_type = self.picking_id.picking_type_id.return_picking_type_id
            if return_picking_type.default_location_dest_id.return_location:
                location_id = return_picking_type.default_location_dest_id.id
            self.location_id = location_id

    def create_returns(self):
        """Override create_returns method for creating one or more
        'confirmed' RMAs after return a delivery picking in case
        'Create RMAs' checkbox is checked in this wizard.
        New RMAs will be linked to the delivery picking as the origin
        delivery and also RMAs will be linked to the returned picking
        as the 'Receipt'.
        """
        if self.create_rma:
            # set_rma_picking_type is to override the copy() method of stock
            # picking and change the default picking type to rma picking type
            self_with_context = self.with_context(set_rma_picking_type=True)
            res = super(ReturnPicking, self_with_context).create_returns()
            if not self.picking_id.partner_id:
                raise ValidationError(
                    _(
                        "You must specify the 'Customer' in the "
                        "'Stock Picking' from which RMAs will be created"
                    )
                )
            returned_picking = self.env["stock.picking"].browse(res["res_id"])
            vals_list = [
                move._prepare_return_rma_vals(self.picking_id)
                for move in returned_picking.move_ids
            ]
            self.env["rma"].create(vals_list)
            return res
        else:
            return super().create_returns()
