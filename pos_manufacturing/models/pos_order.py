# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from datetime import datetime,timezone
from functools import partial
import re
import psycopg2
import logging

_logger = logging.getLogger(__name__)


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    note = fields.Char('Internal Note added by the waiter.')


class PosOrder(models.Model):
    _inherit = "pos.order"

    table_id = fields.Many2one('manufacturing.table', string='Table', help='The table where this order was served', index='btree_not_null', readonly=True)
    customer_count = fields.Integer(string='Guests', help='The amount of customers that have been served by this order.', readonly=True)

    @api.model
    def _process_order(self, order, draft, existing_order):
        order_data = order['data']
        pos_session = self.env['pos.session'].browse(order_data['pos_session_id'])
        if pos_session.state in ['closing_control', 'closed']:
            order_data['pos_session_id'] = self._get_valid_session(order_data).id
        
        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order_data))
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order_data['user_id'] = pos_order.user_id.id
            pos_order.write(self._order_fields(order_data))

        self._create_pos_order_lines(order_data, pos_order)
        pos_order = pos_order.with_company(pos_order.company_id)
        self = self.with_company(pos_order.company_id)
        self._process_payment_lines(order_data, pos_order, pos_session, draft)

        if not draft:
            self._finalize_pos_order(pos_order)

        # Additional logic for creating MRP Orders if needed
        if pos_order.config_id.create_mrp_order:
            self._create_mrp_orders(pos_order)

        return pos_order.id

    def _create_pos_order_lines(self, order_data, pos_order):
        if order_data['lines']:
            for line_data in order_data['lines']:
                line_vals = line_data[2]  # Assuming order['lines'] contains line data in the third position
                if line_vals.get('is_modifier'):
                    self._handle_modifier_lines(line_vals, pos_order)
                else:
                    # Additional logic 
                    pass

    def _handle_modifier_lines(self, line_vals, pos_order):
        if 'is_laterality' in line_vals and line_vals['is_laterality']:
            for prod in line_vals['is_modifier']:
                qty = prod['qty']
                if not prod.get('is_sub', False):
                    if prod['side_type'] == 'left':
                        qty = prod['qty'] / 2
                    elif prod['side_type'] == 'right':
                        qty = prod['qty'] / 4
                
                product_id = self.env['product.product'].browse(prod['id'])
                self.env['pos.order.line'].create({
                    'name': self.env['ir.sequence'].next_by_code('pos.order.line'),
                    'discount': 0,
                    'product_id': product_id.id,
                    'full_product_name': prod['display_name'],
                    'price_subtotal': 0,
                    'price_unit': 0,
                    'order_id': pos_order.id,
                    'qty': qty,
                    'price_subtotal_incl': 0,
                })

    def _finalize_pos_order(self, pos_order):
        try:
            pos_order.action_pos_order_paid()
        except psycopg2.DatabaseError:
            raise
        except Exception as e:
            _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
        pos_order._create_order_picking()
        if pos_order.to_invoice and pos_order.state == 'paid':
            pos_order.action_pos_order_invoice()

    def _create_mrp_orders(self, pos_order):
        mrp_order_model = self.env['mrp.production']
        for line in pos_order.lines:
            route_ids = line.product_id.route_ids.mapped('name')
            if 'Manufacture' in route_ids and line.product_id.bom_ids:
                mrp_order = mrp_order_model.create({
                    'product_id': line.product_id.id,
                    'product_qty': line.qty,
                    'date_start': fields.Datetime.now(),
                    'user_id': self.env.user.id,
                    'company_id': self.env.company.id,
                })
                mrp_order.action_confirm()
                if pos_order.config_id.mrp_order_done:
                    mrp_order.write({'qty_producing': line.qty})
                    for move_line in mrp_order.move_raw_ids:
                        move_line.write({'quantity_done': move_line.product_uom_qty})
                    mrp_order.button_mark_done()

    @api.model
    def remove_from_ui(self, server_ids):
        tables = self.env['pos.order'].search([('id', 'in', server_ids)]).table_id
        order_ids = super().remove_from_ui(server_ids)
        self.send_table_count_notification(tables)
        return order_ids

    def _process_saved_order(self, draft):
        order_id = super()._process_saved_order(draft)
        self.send_table_count_notification(self.table_id)
        return order_id

    def send_table_count_notification(self, table_ids):
        messages = []
        for config in self.env['pos.config'].search([('floor_ids', 'in', table_ids.floor_id.ids)]):
            config_cur_session = config.current_session_id
            if config_cur_session:
                order_count = config.get_tables_order_count_and_printing_changes()
                messages.append((config_cur_session._get_bus_channel_name(), 'TABLE_ORDER_COUNT', order_count))
        self.env['bus.bus']._sendmany(messages)

    def set_tip(self, tip_line_vals):
        """Set tip to `self` based on values in `tip_line_vals`."""

        self.ensure_one()
        PosOrderLine = self.env['pos.order.line']
        process_line = partial(PosOrderLine._order_line_fields, session_id=self.session_id.id)

        # 1. add/modify tip orderline
        processed_tip_line_vals = process_line([0, 0, tip_line_vals])[2]
        processed_tip_line_vals.update({ "order_id": self.id })
        tip_line = self.lines.filtered(lambda line: line.product_id == self.session_id.config_id.tip_product_id)
        if not tip_line:
            tip_line = PosOrderLine.create(processed_tip_line_vals)
        else:
            tip_line.write(processed_tip_line_vals)

        # 2. modify payment
        payment_line = self.payment_ids.filtered(lambda line: not line.is_change)[0]
        # TODO it would be better to throw error if there are multiple payment lines
        # then ask the user to select which payment to update, no?
        payment_line._update_payment_line_for_tip(tip_line.price_subtotal_incl)

        # 3. flag order as tipped and update order fields
        self.write({
            "is_tipped": True,
            "tip_amount": tip_line.price_subtotal_incl,
            "amount_total": self.amount_total + tip_line.price_subtotal_incl,
            "amount_paid": self.amount_paid + tip_line.price_subtotal_incl,
        })

    def set_no_tip(self):
        """Override this method to introduce action when setting no tip."""
        self.ensure_one()
        self.write({
            "is_tipped": True,
            "tip_amount": 0,
        })

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['table_id'] = ui_order.get('table_id', False)
        order_fields['customer_count'] = ui_order.get('customer_count', 0)
        return order_fields

    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result['table_id'] = order.table_id.id
        result['customer_count'] = order.customer_count
        return result

    @api.model
    def export_for_ui_table_draft(self, table_ids):
        orders = self.env['pos.order'].search([('state', '=', 'draft'), ('table_id', 'in', table_ids)])
        return orders.export_for_ui()
