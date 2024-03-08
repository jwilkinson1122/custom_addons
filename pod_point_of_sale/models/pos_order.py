# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from datetime import datetime,timezone
import re
import psycopg2
import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

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

