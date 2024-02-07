# -*- coding: utf-8 -*-


from odoo import api, Command, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    prescription_order_count = fields.Integer(
        "Count of generated RX",
        compute='_compute_prescription_order_count',
        groups='prescription.group_prescription_user')

    @api.depends('procurement_group_id.stock_move_ids.created_prescription_line_ids.order_id', 'procurement_group_id.stock_move_ids.move_orig_ids.prescription_line_id.order_id')
    def _compute_prescription_order_count(self):
        for production in self:
            production.prescription_order_count = len(production.procurement_group_id.stock_move_ids.created_prescription_line_ids.order_id |
                                                  production.procurement_group_id.stock_move_ids.move_orig_ids.prescription_line_id.order_id)

    def action_view_prescription_orders(self):
        self.ensure_one()
        prescription_order_ids = (self.procurement_group_id.stock_move_ids.created_prescription_line_ids.order_id | self.procurement_group_id.stock_move_ids.move_orig_ids.prescription_line_id.order_id).ids
        action = {
            'res_model': 'prescription.order',
            'type': 'ir.actions.act_window',
        }
        if len(prescription_order_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': prescription_order_ids[0],
            })
        else:
            action.update({
                'name': _("Prescription Order generated from %s", self.name),
                'domain': [('id', 'in', prescription_order_ids)],
                'view_mode': 'tree,form',
            })
        return action

    def _get_document_iterate_key(self, move_raw_id):
        iterate_key = super(MrpProduction, self)._get_document_iterate_key(move_raw_id)
        if not iterate_key and move_raw_id.created_prescription_line_ids:
            iterate_key = 'created_prescription_line_ids'
        return iterate_key

    def _prepare_merge_orig_links(self):
        origs = super()._prepare_merge_orig_links()
        for move in self.move_raw_ids:
            if not move.move_orig_ids or not move.created_prescription_line_ids:
                continue
            origs[move.bom_line_id.id].setdefault('created_prescription_line_ids', set()).update(move.created_prescription_line_ids.ids)
        for vals in origs.values():
            if vals.get('created_prescription_line_ids'):
                vals['created_prescription_line_ids'] = [Command.set(vals['created_prescription_line_ids'])]
            else:
                vals['created_prescription_line_ids'] = []
        return origs
