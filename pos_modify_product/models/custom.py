# -*- coding: utf-8 -*-


from odoo import models,fields,api,tools,_
from datetime import datetime,timezone
import re
import psycopg2
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
	_inherit = 'product.template'
      
	bom_product = fields.Boolean(
		string='POS BOM Product')
	modifier_ok = fields.Boolean(string='Modifier Product')
	device_laterality = fields.Boolean(string='Display Device Laterality?')
	modifier_groups_ids = fields.Many2many("modifier.product", string="Modifier Groups")
	sub_products_ids = fields.Many2many("product.product", string="Sub Products")
	modifier_attribute_product_id = fields.One2many('modifier.attribute','product_temp_id',string='Modifier Attribute')
	
	def get_modifiers(self):
		modifierAttribute = self.env['modifier.attribute']
		modifier_group = self.modifier_groups_ids
		for modifier in modifier_group:
			for product in modifier.modifier_product_id:
				for attr in product.with_prefetch().product_variant_ids:
					product_record = self.env['product.product'].browse(attr.id) 
					name = product_record.display_name
					output = name[name.find("(")+1:name.rfind(")")]
					
					vals = {
						'product_id':attr.id,
						'product_temp_id': self.id,
						'price':attr.lst_price,
						'display_name':output
					}
					is_exist = modifierAttribute.search([('product_id', '=', vals['product_id'])])
					if is_exist:
						pass
					else:
						modifierAttributeRecord = modifierAttribute.create(vals)



class PosConfigInherit(models.Model):
	_inherit = "pos.config"

	product_configure = fields.Boolean(string="Allow Product Configure",default=True)


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	product_configure = fields.Boolean(related='pos_config_id.product_configure', readonly=False)


# class pos_order(models.Model):
# 	_inherit = 'pos.order'

# 	@api.model
# 	def _process_order(self, order, draft, existing_order):
# 		order = order['data']
# 		pos_session = self.env['pos.session'].browse(order['pos_session_id'])
# 		if pos_session.state == 'closing_control' or pos_session.state == 'closed':
# 			order['pos_session_id'] = self._get_valid_session(order).id

# 		pos_order = False
# 		if not existing_order:
# 			pos_order = self.create(self._order_fields(order))
# 		else:
# 			pos_order = existing_order
# 			pos_order.lines.unlink()
# 			order['user_id'] = pos_order.user_id.id
# 			pos_order.write(self._order_fields(order))

# 		if order['lines']:
# 			for l in order['lines']:
# 				if l[2].get('is_modifier'):
# 					if 'is_laterality' in l[2]:
# 						if l[2]['is_laterality']:
# 							for prod in l[2]['is_modifier']:
# 								if 'is_sub' in prod:
# 									qty = prod['qty']
# 								else:
# 									if (prod['segment_type'] == 'bilateral'):
# 										qty = prod['qty']/2
# 									else:
# 										qty = prod['qty']

# 								product_id = self.env['product.product'].browse(prod['id'])
# 								self.env['pos.order.line'].create({
# 									'name':self.env['ir.sequence'].next_by_code('pos.order.line'),
# 									'discount': 0, 
# 									'product_id': product_id.id,
# 									'full_product_name': prod['display_name'],
# 									'price_subtotal': 0,
# 									'price_unit': 0,
# 									'order_id' : pos_order.id,
# 									'qty': qty,
# 									'price_subtotal_incl': 0,
# 								})

# 		pos_order = pos_order.with_company(pos_order.company_id)
# 		self = self.with_company(pos_order.company_id)
# 		self._process_payment_lines(order, pos_order, pos_session, draft)

# 		if not draft:
# 			try:
# 				pos_order.action_pos_order_paid()
# 			except psycopg2.DatabaseError:
# 				raise
# 			except Exception as e:
# 				_logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
# 			pos_order._create_order_picking()

# 		if pos_order.to_invoice and pos_order.state == 'paid':
# 			pos_order.action_pos_order_invoice()

# 		return pos_order.id


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _process_order(self, pos_order_data, draft, existing_order):
        pos_order = pos_order_data['data']
        result = super(PosOrder, self)._process_order(pos_order_data, draft, existing_order)

        # Handle session validity
        pos_session = self.env['pos.session'].browse(pos_order['pos_session_id'])
        if pos_session.state in ['closing_control', 'closed']:
            pos_order['pos_session_id'] = self._get_valid_session(pos_order).id

        # Initialize or update the order
        if not existing_order:
            pos_order_instance = self.create(self._order_fields(pos_order))   
        else:
            existing_order.lines.unlink()
            pos_order_instance = existing_order
            pos_order['user_id'] = existing_order.user_id.id
            existing_order.write(self._order_fields(pos_order))

        # Process modifiers
        if pos_order.get('lines'):
            self._process_order_lines(pos_order['lines'], pos_order_instance)

        # Handle payments and invoicing
        pos_order_instance = pos_order_instance.with_company(pos_order_instance.company_id)
        self._process_payment_lines(pos_order, pos_order_instance, pos_session, draft)

        if not draft:
            self._finalize_order(pos_order_instance, pos_order)

        return pos_order_instance.id

    def _process_order_lines(self, lines, order_instance):
        for line in lines:
            if line[2].get('is_modifier'):
                for prod in line[2]['is_modifier']:
                    qty = prod['qty'] * 2 if prod.get('laterality_type') == 'bilateral' else prod['qty']
                    product_id = self.env['product.product'].browse(prod['id'])
                    self.env['pos.order.line'].create({
                        'name': self.env['ir.sequence'].next_by_code('pos.order.line'),
                        'discount': 0,
                        'product_id': product_id.id,
                        'full_product_name': prod['display_name'],
                        'price_subtotal': 0,
                        'price_unit': 0,
                        'order_id': order_instance.id,
                        'qty': qty,
                        'price_subtotal_incl': 0,
                    })

    def _finalize_order(self, order_instance, pos_order):
        try:
            order_instance.action_pos_order_paid()
        except psycopg2.DatabaseError:
            raise
        except Exception as e:
            _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
        
        order_instance._create_order_picking()
        order_instance._compute_total_cost_in_real_time()

        if pos_order.get('to_invoice', False) and order_instance.state == 'paid' and order_instance.amount_total > 0:
            order_instance.action_pos_order_invoice()




class POSSession(models.Model):
	_inherit = 'pos.session'

	def _loader_params_product_product(self):
		res = super(POSSession, self)._loader_params_product_product()
		fields = res.get('search_params').get('fields')
		fields.extend(['product_template_attribute_value_ids','modifier_attribute_product_id','device_laterality','sub_products_ids'])
		res['search_params']['fields'] = fields
		return res


	def _pos_ui_models_to_load(self):
		result = super()._pos_ui_models_to_load()
		result.extend(['product.template','modifier.attribute'])
		return result

	def _loader_params_product_template(self):
		return {
			'search_params': {
				'domain': [('sale_ok','=',True),('available_in_pos','=',True)],
				'fields': ['name','display_name','product_variant_ids','product_variant_count']
			}
		}

	def _get_pos_ui_product_template(self, params):
		return self.env['product.template'].search_read(**params['search_params'])



	def _loader_params_modifier_attribute(self):
		return {
			'search_params': {
				'domain': [], 
				'fields': ['name','product_id','price','uom_id','display_name']
			}
		}

	def _get_pos_ui_modifier_attribute(self, params):
		return self.env['modifier.attribute'].search_read(**params['search_params'])