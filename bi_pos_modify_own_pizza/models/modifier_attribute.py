# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api,_
from datetime import datetime,timezone


class ModifierAttribute(models.Model):
	_name = 'modifier.attribute'
	_description = "Modifier Attribute"
	
	product_id = fields.Many2one(comodel_name='product.product', string='Product',domain=[('available_in_pos', '=' ,True)], required=True)
	product_temp_id = fields.Many2one(comodel_name='product.template', string='Product', required=True)
	
	price = fields.Float(related='product_id.lst_price', string='Price')
	uom_id = fields.Many2one(related='product_id.uom_id' , string="Unit of Measure", readonly="1")
	name = fields.Char(related='product_id.name', string="Product Name",readonly="1")
	display_name = fields.Char(string="Varinat name")