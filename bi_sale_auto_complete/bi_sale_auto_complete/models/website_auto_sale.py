# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from datetime import date,datetime
from odoo.exceptions import UserError, ValidationError

class InheritPartner(models.Model):
	_inherit = "res.partner"

	web_work_process_id = fields.Many2one("website.auto.sale",string="Website Workflow Process")


class WebsiteAutoSale(models.Model):
	_name = "website.auto.sale"
	_description = "Website Auto Sale"

	name = fields.Char(string="Name")	
	company_id = fields.Many2one('res.company', string='Company')
	
	validation_order = fields.Boolean("Validation Order")
	
	validation_picking = fields.Boolean("Validation Picking")
	
	create_incoice = fields.Boolean("Create Invoice")
	validate_invoice = fields.Boolean("Vaidate Invoice")

	@api.onchange('validate_invoice')
	def depends_force(self):
		if self.validate_invoice == True:
			self.create_incoice = True	
	
	@api.onchange('validation_picking')
	def depends_transfer(self):
		if self.validation_picking == True:
			self.validation_order = True

	@api.onchange('create_incoice')
	def depends_invoice(self):
		if self.create_incoice == True:
			self.validation_order = True
			self.validation_picking = True


class InheritSale(models.Model):
	_inherit = "sale.order"

	web_work_process_id = fields.Many2one("website.auto.sale",string="Website Workflow Process",related="partner_id.web_work_process_id")

	def action_auto_sale(self):
		if self.partner_id.web_work_process_id:
			web_work_process_id = self.partner_id.web_work_process_id
			if web_work_process_id.validation_order == True:
				picking_confirm=self.action_confirm()
				for order in self:
					if web_work_process_id.validation_picking == True :
						picking_obj = self.env['stock.picking'].search([('origin','=',order.name)])
						
						for pick in picking_obj:
							for qty in pick.move_lines:
								qty.write({
									'quantity_done' : qty.product_uom_qty
								})
							
							pick.button_validate()
							pick._action_done()

							for line in order.order_line:
								line.write({
									'qty_delivered' : line.product_uom_qty,
								})

				if web_work_process_id.create_incoice == True:
					create_invoice = self._create_invoices()
					invoice_obj = self.env['account.move'].search([('invoice_origin','=',self.name)])
					if web_work_process_id.validate_invoice == True:
						validate=invoice_obj.action_post()
		else:
			raise Warning(('Workflow Process is not given,Please give the Website Workflow process.') )

		
		