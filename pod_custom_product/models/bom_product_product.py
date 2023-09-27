# -*- coding: utf-8 -*-


from odoo import models,fields,api,_
from datetime import datetime,timezone


class BOMProduct(models.Model):
	_name = 'bom.product'
	_description="bom product"

	
	state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('cancel', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")

	name = fields.Char(string="Sequence Number", store=True, required=True,)

	bom_product_id = fields.Many2one(
		'product.product',
		string='BOM Product',domain="[('bom_product', '=', True),('available_in_pos', '=', True)]",required=True,
	)

	qty = fields.Integer(
		string='Product Quantity',default=1,required=True,
	)

	product_uom_id = fields.Many2one(
		'uom.uom',
		string='Product UOM',required=True,
	)

	sub_products_ids = fields.One2many(
		'bom.product.line',
		'sub_product_id',
		string='o2m of product temp',
	)

	@api.onchange('bom_product_id')
	def onchange_bom_product(self):
		values = {}
		self.product_uom_id = self.bom_product_id.uom_id

		name = self.bom_product_id.name
		if (name):
			self.name = name + '-Structure'


	def consirm_bom_product(self):
		self.state = 'confirm'

	def set_to_draft(self):
		self.state = 'draft'

	def set_to_cancel(self):
		self.state = 'cancel'

class BOMProduct(models.Model):
	_name = 'bom.product.line'
	_description="bom product"

	

	sub_product_id = fields.Many2one(
		'bom.product',
		string='m2o of product pro',
	)

	product_id = fields.Many2one(
		'product.product',
		string='Product',domain="[('available_in_pos', '=', True)]"
	)

	qty = fields.Integer(
		string='Product Quantity',default=1,required=True,
	)

	product_uom_id = fields.Many2one(
		'uom.uom',
		string='Product UOM',required=True,
	)

	@api.onchange('product_id')
	def onchange_product(self):
		values = {}
		self.product_uom_id = self.product_id.uom_id