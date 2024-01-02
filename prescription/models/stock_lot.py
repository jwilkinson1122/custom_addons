# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, fields, models, _


class StockLot(models.Model):
    _inherit = 'stock.lot'

    prescription_line_ids = fields.Many2many('prescription.order', string="Prescription Orders", compute="_compute_prescription_line_ids")
    prescription_part_count = fields.Integer('Prescription part count', compute="_compute_prescription_line_ids")
    in_prescription_count = fields.Integer('In prescription count', compute="_compute_in_prescription_count")
    done_count = fields.Integer('Done count', compute='_compute_done_count')

    @api.depends('name')
    def _compute_prescription_line_ids(self):
        prescription_orders = defaultdict(lambda: self.env['prescription.order'])
        prescription_moves = self.env['stock.move'].search([
            ('prescription_id', '!=', False),
            ('prescription_line_type', '!=', False),
            ('move_line_ids.lot_id', 'in', self.ids),
            ('state', '=', 'done')])
        for prescription_line in prescription_moves:
            for rl_id in prescription_line.lot_ids.ids:
                prescription_orders[rl_id] |= prescription_line.prescription_id
        for lot in self:
            lot.prescription_line_ids = prescription_orders[lot.id]
            lot.prescription_part_count = len(lot.prescription_line_ids)

    def _compute_in_prescription_count(self):
        lot_data = self.env['prescription.order']._read_group([('lot_id', 'in', self.ids), ('state', 'not in', ('done', 'cancel'))], ['lot_id'], ['__count'])
        result = {lot.id: count for lot, count in lot_data}
        for lot in self:
            lot.in_prescription_count = result.get(lot.id, 0)

    def _compute_done_count(self):
        lot_data = self.env['prescription.order']._read_group([('lot_id', 'in', self.ids), ('state', '=', 'done')], ['lot_id'], ['__count'])
        result = {lot.id: count for lot, count in lot_data}
        for lot in self:
            lot.done_count = result.get(lot.id, 0)

    def action_lot_open_prescriptions(self):
        action = self.env["ir.actions.actions"]._for_xml_id("prescription.action_prescription_order_tree")
        action.update({
            'domain': [('lot_id', '=', self.id)],
            'context': {
                'default_product_id': self.product_id.id,
                'default_lot_id': self.id,
                'default_company_id': self.company_id.id,
            },
        })
        return action

    def action_view_rx(self):
        self.ensure_one()

        action = {
            'res_model': 'prescription.order',
            'type': 'ir.actions.act_window'
        }
        if len(self.prescription_line_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.prescription_line_ids[0].id
            })
        else:
            action.update({
                'name': _("Prescription orders of %s", self.name),
                'domain': [('id', 'in', self.prescription_line_ids.ids)],
                'view_mode': 'tree,form'
            })
        return action
