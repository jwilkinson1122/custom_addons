from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _action_apply_inventory(self, product_id, product_stock_uom_id, product_qty, operation='remove'):
        """Update on hand qty."""

        self.ensure_one()

        # Check if has storable product and is linked to a task
        if self.task_id and product_id.type == 'product':
            
            # Get quant of product
            quant = self.env['stock.quant'].search([
                ('product_id', '=', product_id.id),
            ], limit=1)

            # Convert uom
            line_quantity = product_stock_uom_id._compute_quantity(product_qty, product_id.uom_id, rounding_method='HALF-UP')

            # Remove quantity
            if operation == 'remove':
                if (quant.quantity - line_quantity) < 0.0:
                    raise UserError(_("Cannot apply inventory change for %s as result would be negative.") % product_id.display_name)
                quant.inventory_quantity = quant.quantity - line_quantity
                quant.action_apply_inventory()
            
            # Add quantity
            if operation == 'add':
                if quant.quantity < 0.0:
                    raise UserError(_("No empty or positive inventory has been found for product %s.") % product_id.display_name)
                quant.inventory_quantity = quant.quantity + line_quantity
                quant.action_apply_inventory()

    def action_validate_timesheet(self):
        """Set product qty if timesheet entry is validated."""
        for line in self:
            line._action_apply_inventory(product_id=line.product_id, product_stock_uom_id=line.product_stock_uom_id, product_qty=line.product_qty)
            if line.product_dest_id:
                line._action_apply_inventory(product_id=line.product_dest_id, product_stock_uom_id=line.product_dest_stock_uom_id, product_qty=line.product_dest_qty, operation='add')
        return super().action_validate_timesheet()

    def action_invalidate_timesheet(self):
        """Undo inventory change if move is invalidated."""
        res = super().action_invalidate_timesheet()
        for line in self:
            line._action_apply_inventory(product_id=line.product_id, product_stock_uom_id=line.product_stock_uom_id, product_qty=line.product_qty, operation='add')
            if line.product_dest_id:
                line._action_apply_inventory(product_id=line.product_dest_id, product_stock_uom_id=line.product_dest_stock_uom_id, product_qty=line.product_dest_qty)
        # self.write({'validated': False})
        return res