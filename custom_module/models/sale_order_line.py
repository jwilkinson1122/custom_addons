import logging
from odoo.addons.sale_stock.models.sale_order import SaleOrderLine as\
    OriginalSaleOrderLine
from odoo.tools import float_compare
from odoo import fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    procurement_express_group_id = fields.Many2one(
        comodel_name='procurement.group', string='Procurement express Group',
        copy=False)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    express_shipping = fields.Boolean()

    def _get_procurement_express_group(self):
        return self.order_id.procurement_express_group_id

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method with required/custom fields
         genrated by a sale order line. procurement group will launch
          '_run_pull', '_run_buy' or '_run_manufacture' depending on
           the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        procurements = []
        express_lines_amnt = 0
        for line in self:
            if line.express_shipping:
                express_lines_amnt += 1
        for line in self:
            if line.state != 'sale' or line.product_id.type not in (
                    'consu', 'product'):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty,
                             precision_digits=precision) >= 0:
                continue
            values = False
            if not line.express_shipping:
                group_id = line._get_procurement_group()
                if not group_id:
                    group_id = self.env['procurement.group'].create(
                        line._prepare_procurement_group_vals())
                    line.order_id.procurement_group_id = group_id
                else:
                    # In case the procurement group is already created and
                    # the order was
                    # cancelled, we need to update certain values of the group.
                    updated_vals = {}
                    if group_id.partner_id != \
                            line.order_id.partner_shipping_id:
                        updated_vals.update(
                            {'partner_id': line.order_id.partner_shipping_id.id
                             })
                    if group_id.move_type != line.order_id.picking_policy:
                        updated_vals.update(
                            {'move_type': line.order_id.picking_policy})
                    if updated_vals:
                        group_id.write(updated_vals)
                values = line._prepare_procurement_values(group_id=group_id)
            if line.express_shipping and express_lines_amnt >= 2:
                express_group_id = line._get_procurement_express_group()
                if not express_group_id:
                    express_group_id = self.env['procurement.group'].create(
                        line._prepare_procurement_group_vals())
                    line.order_id.procurement_express_group_id = \
                        express_group_id
                else:
                    updated_vals = {}
                    if express_group_id.partner_id != line.order_id.\
                            partner_shipping_id:
                        updated_vals.update({
                            'partner_id':
                                line.order_id.partner_shipping_id.id})
                    if express_group_id.move_type != \
                            line.order_id.picking_policy:
                        updated_vals.update(
                            {'move_type': line.order_id.picking_policy})
                    if updated_vals:
                        express_group_id.write(updated_vals)
                values = line._prepare_procurement_values(
                    group_id=express_group_id)
            product_qty = line.product_uom_qty - qty
            line_uom = line.product_uom
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                product_qty, line.product_id.uom_id)
            if not line.express_shipping or line.express_shipping \
                    and express_lines_amnt >= 2:
                procurements.append(self.env['procurement.group'].Procurement(
                    line.product_id, product_qty, procurement_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.name, line.order_id.name, line.order_id.company_id,
                    values))
        if procurements:
            self.env['procurement.group'].run(procurements)
        return True

    OriginalSaleOrderLine._action_launch_stock_rule = _action_launch_stock_rule
