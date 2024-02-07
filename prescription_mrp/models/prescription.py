# -*- coding: utf-8 -*-


from collections import defaultdict

from odoo import api, fields, models, _
from odoo.tools import OrderedSet


class PrescriptionOrder(models.Model):
    _inherit = 'prescription.order'

    mrp_production_count = fields.Integer(
        "Count of MO Source",
        compute='_compute_mrp_production_count',
        groups='mrp.group_mrp_user')

    @api.depends('order_line.move_dest_ids.group_id.mrp_production_ids')
    def _compute_mrp_production_count(self):
        for prescription in self:
            prescription.mrp_production_count = len(prescription._get_mrp_productions())

    def _get_mrp_productions(self, **kwargs):
        return self.order_line.move_dest_ids.group_id.mrp_production_ids | self.order_line.move_ids.move_dest_ids.group_id.mrp_production_ids

    def action_view_mrp_productions(self):
        self.ensure_one()
        mrp_production_ids = self._get_mrp_productions().ids
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
        }
        if len(mrp_production_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': mrp_production_ids[0],
            })
        else:
            action.update({
                'name': _("Manufacturing Source of %s", self.name),
                'domain': [('id', 'in', mrp_production_ids)],
                'view_mode': 'tree,form',
            })
        return action


class PrescriptionOrderLine(models.Model):
    _inherit = 'prescription.order.line'

    def _compute_qty_received(self):
        kit_lines = self.env['prescription.order.line']
        lines_stock = self.filtered(lambda l: l.qty_received_method == 'stock_moves' and l.move_ids and l.state != 'cancel')
        product_by_company = defaultdict(OrderedSet)
        for line in lines_stock:
            product_by_company[line.company_id].add(line.product_id.id)
        kits_by_company = {
            company: self.env['mrp.bom']._bom_find(self.env['product.product'].browse(product_ids), company_id=company.id, bom_type='phantom')
            for company, product_ids in product_by_company.items()
        }
        for line in lines_stock:
            kit_bom = kits_by_company[line.company_id].get(line.product_id)
            if kit_bom:
                moves = line.move_ids.filtered(lambda m: m.state == 'done' and not m.scrapped)
                order_qty = line.product_uom._compute_quantity(line.product_uom_qty, kit_bom.product_uom_id)
                filters = {
                    'incoming_moves': lambda m: m.location_id.usage == 'supplier' and (not m.origin_returned_move_id or (m.origin_returned_move_id and m.to_refund)),
                    'outgoing_moves': lambda m: m.location_id.usage != 'supplier' and m.to_refund
                }
                line.qty_received = moves._compute_kit_quantities(line.product_id, order_qty, kit_bom, filters)
                kit_lines += line
        super(PrescriptionOrderLine, self - kit_lines)._compute_qty_received()

    def _get_upstream_documents_and_responsibles(self, visited):
        return [(self.order_id, self.order_id.user_id, visited)]

    def _get_qty_procurement(self):
        self.ensure_one()
        # Specific case when we change the qty on a RX for a kit product.
        # We don't try to be too smart and keep a simple approach: we compare the quantity before
        # and after update, and return the difference. We don't take into account what was already
        # sent, or any other exceptional case.
        bom = self.env['mrp.bom'].sudo()._bom_find(self.product_id, bom_type='phantom')[self.product_id]
        if bom and 'previous_product_qty' in self.env.context:
            return self.env.context['previous_product_qty'].get(self.id, 0.0)
        return super()._get_qty_procurement()
