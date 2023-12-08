# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class createsaleorder(models.TransientModel):
	_name = 'create.saleorder'
	_description = "Create Sale Order"


	new_order_line_ids = fields.One2many( 'getprescription.orderdata', 'new_order_line_id', string="Order Line")
	
	partner_id = fields.Many2one('res.partner', string='Customer', required=True)
	date_order = fields.Datetime(string='Order Date', required=True, default=fields.Datetime.now)
	


	@api.model
	def default_get(self,  default_fields):
		res = super(createsaleorder, self).default_get(default_fields)
		record = self.env['prescriptions.order'].browse(self._context.get('active_ids',[]))
		update = []
		for record in record.order_line:
			update.append((0,0,{
					'product_id' : record.product_id.id,
					'name' : record.name,
					'product_uom_qty' : record.product_uom_qty,
					'price_unit' : record.price_unit,
					'price_subtotal' : record.price_subtotal,
     				# 'commitment_date' : record.commitment_date,
					# 'commitment_date' : datetime.today(),
				}))

			res.update({'new_order_line_ids':update})
		return res	



	def action_create_sale_order(self):
		self.ensure_one()
		res = self.env['sale.order'].browse(self._context.get('id',[]))
		value = [] 
		for data in self.new_order_line_ids:
			value.append([0,0,{
								'product_id' : data.product_id.id,
								'name' : data.name,
								'product_uom_qty' : data.product_uom_qty,
								'price_unit' : data.price_unit,
								}])
		res.create({	'partner_id' : self.partner_id.id,
						'date_order' : self.date_order,
						'order_line':value,
						
					})
		return 


class getprescriptionorder(models.TransientModel):
	_name = 'getprescription.orderdata'
	_description = "Get prescription Order Data"


	new_order_line_id = fields.Many2one('create.saleorder')
	
	product_id = fields.Many2one('product.product', string="Product", required=True)
	name = fields.Char(string="Description", required=True)
	product_uom_qty = fields.Float(string='Quantity', required=True)
	price_unit = fields.Float(string="Unit Price", required = True)
	price_subtotal = fields.Float(string="Sub Total", compute='_compute_total')
	# commitment_date = fields.Datetime(string='Receipt Date')


	@api.depends('product_uom_qty', 'price_unit')
	def _compute_total(self):
		for record in self:
			record.price_subtotal = record.product_uom_qty * record.price_unit

