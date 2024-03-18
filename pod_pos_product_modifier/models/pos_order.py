# -*- coding: utf-8 -*-


from odoo import models, api, tools, _
import psycopg2
import logging

_logger = logging.getLogger(__name__)


class pos_order(models.Model):
	_inherit = 'pos.order'


	@api.model
	def _process_order(self, order, draft, existing_order):
		"""Create or update an pos.order from a given dictionary.

		:param dict order: dictionary representing the order.
		:param bool draft: Indicate that the pos_order is not validated yet.
		:param existing_order: order to be updated or False.
		:type existing_order: pos.order.
		:returns: id of created/updated pos.order
		:rtype: int
		"""
		order = order['data']
		pos_session = self.env['pos.session'].browse(order['pos_session_id'])
		if pos_session.state == 'closing_control' or pos_session.state == 'closed':
			order['pos_session_id'] = self._get_valid_session(order).id

		pos_order = False
		if not existing_order:
			pos_order = self.create(self._order_fields(order))
		else:
			pos_order = existing_order
			pos_order.lines.unlink()
			order['user_id'] = pos_order.user_id.id
			pos_order.write(self._order_fields(order))

		if order['lines']:
			for l in order['lines']:
				if l[2].get('is_modifier'):
					if 'is_laterality' in l[2]:
						if l[2]['is_laterality']:
							for prod in l[2]['is_modifier']:
								if (prod['laterality_type'] == 'bilateral'):
									qty = prod['qty'] * 2
								else:
									qty = prod['qty']
								product_id = self.env['product.product'].browse(prod['id'])
								self.env['pos.order.line'].create({
									'name':self.env['ir.sequence'].next_by_code('pos.order.line'),
									'discount': 0, 
									'product_id': product_id.id,
									'full_product_name': prod['display_name'],
									'price_subtotal': 0,
									'price_unit': 0,
									'order_id' : pos_order.id,
									'qty': qty,
									'price_subtotal_incl': 0,
								})

		pos_order = pos_order.with_company(pos_order.company_id)
		self = self.with_company(pos_order.company_id)
		self._process_payment_lines(order, pos_order, pos_session, draft)

		if not draft:
			try:
				pos_order.action_pos_order_paid()
			except psycopg2.DatabaseError:
				# do not hide transactional errors, the order(s) won't be saved!
				raise
			except Exception as e:
				_logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
			pos_order._create_order_picking()

		if pos_order.to_invoice and pos_order.state == 'paid':
			pos_order.action_pos_order_invoice()

		return pos_order.id
