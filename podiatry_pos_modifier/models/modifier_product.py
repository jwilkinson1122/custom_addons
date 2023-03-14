# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
from datetime import datetime,timezone


class BOMProduct(models.Model):
	_name = 'modifier.product'
	_description="modifier group"


	name = fields.Char('Toppings', required=True)
	modifier_product_id = fields.Many2many("product.template", string="Modifier",domain=[('modifier_ok', '=' ,True)])

	
	