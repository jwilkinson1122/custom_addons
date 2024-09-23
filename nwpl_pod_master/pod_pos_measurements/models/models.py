import logging
import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_custom_product = fields.Boolean(string='Custom Product')
    device_laterality = fields.Boolean(string='Display Foot Side')
    allow_measurements = fields.Boolean(string="Allow Measurements")
    measurement_cat_ids = fields.Many2many('measurement.measurement.category', string='Measurement Categories')

class MeasurementCategory(models.Model):
    _name = 'measurement.measurement.category'
    _description = "Measurement Category"

    name = fields.Char('Name', required=True)
    date = fields.Date(string='Date', default=fields.Date.today(), tracking=True)
    category_id = fields.Many2one('pos.category', string='Category', required=True)
    active = fields.Boolean('Active', default=True)
    measurement_types = fields.Many2many('measurement.type', string='Meaurement Types')
    measurement_ids = fields.One2many('measurement.measurement', 'category_id', string='Measurements')
    measurement_unit = fields.Many2one('uom.uom', string='Measurement Unit', required=True)
    # sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')

    @api.onchange('category_id', 'measurement_types')
    def _onchange_category_id(self):
        if self.category_id:
            self.category_id.write({'measurement_type_ids': [(6, 0, self.measurement_types.ids)]})

    @api.constrains('measurement_types')
    def validate_measurement_types_count(self):
        if len(self.measurement_types) == 0:
            raise ValidationError("Please add at least one measurement type in the measurement group")

class Measurement(models.Model):
    _name = 'measurement.measurement'
    _description = "Order Measurement"
    _rec_name = 'name'

    name = fields.Char(compute="_compute_measurement_name")
    date = fields.Date(string='Date', default=fields.Date.today(), tracking=True)
    active = fields.Boolean('Active', default=True)
    sequence_number = fields.Integer('Sequence Number')
    partner_id = fields.Many2one('res.partner', string="Partner")
    measurement_cat_ids = fields.Many2many('measurement.measurement.category', string='Available In Measurement Categories')
    category_id = fields.Many2one('measurement.measurement.category', string='Category')
    measurement = fields.Char('Measurement')
    measurement_type = fields.Many2one('measurement.type', string='Meaurement Type', required=True)
    measurement_unit = fields.Many2one('uom.uom', string='Measurement Unit', required=True)
    pos_extra_price = fields.Float('Extra Price', default=0)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id.id)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')
    laterality = fields.Many2one('product.attribute.value', string="Laterality", domain="[('attribute_id', '=', ref('product_attribute_laterality'))]")

    @api.constrains('pos_extra_price')
    def validate_extra_price(self):
        for record in self:
            if record.pos_extra_price < 0:
                raise ValidationError("Extra Price cannot be less than zero.")
    
    @api.depends('measurement_type', 'measurement', 'laterality')
    def _compute_measurement_name(self):
        for rec in self:
            laterality_name = rec.laterality.name if rec.laterality else ''
            rec.name = f"{rec.measurement_type.name}: {rec.measurement} {laterality_name}" if rec.measurement_type and rec.measurement else False

            
    # @api.depends('measurement_type', 'measurement')
    # def _compute_measurement_name(self):
    #     for rec in self:
    #         rec.name = f"{rec.measurement_type.name}: {rec.measurement}" if rec.measurement_type and rec.measurement else False

class MeasurementType(models.Model):
    _name = 'measurement.type'
    _description = "Types of Measurements"

    name = fields.Text('Measurement', required=True)
    active = fields.Boolean('Active', default=True)
    sequence_number = fields.Integer('Sequence Number')
    measurement_cat_ids = fields.Many2many('measurement.measurement.category', string='Available In Measurement Categories', readonly=True,)
    pos_extra_price = fields.Float('Extra Price', default=0)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id.id)

    @api.constrains('pos_extra_price')
    def validate_extra_price(self):
        for record in self:
            if record.pos_extra_price < 0:
                raise ValidationError("Extra Price cannot be less than zero.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'sequence_number' not in vals:
                vals['sequence_number'] = self.env['ir.sequence'].next_by_code('measurement.type')
        return super().create(vals_list)

class ProductUOMPrice(models.Model):
    _name = 'product.uom.price'
    _description = 'Product UOM Price'

    variant = fields.Many2one('product.template', 'Product')
    uom_id = fields.Many2one('uom.uom', 'UOM', required=True, domain=[('category_id.is_custom_product', '=', True)])
    qty = fields.Float('Qty')
    unit_price = fields.Float('Unit Price')
    price = fields.Float('Price')

class UomCategory(models.Model):
    _inherit = 'uom.category'

    is_custom_product = fields.Boolean('Custom Product')

class PosCategory(models.Model):
    _inherit = 'pos.category'

    @api.model
    def _default_measurement_unit(self):
        return self.env.ref('uom.product_uom_unit', False).id if self.env.ref('uom.product_uom_unit', False) else False

    # measurement_type_ids = fields.Many2many('measurement.type', string="Meaurement Type")
    # measurement_unit = fields.Many2one('uom.uom', string="Measurement Unit", default=lambda self: self.env.ref('uom.product_uom_unit', False).id if self.env.ref('uom.product_uom_unit', False) else False)

    measurement_type_ids = fields.Many2many('measurement.type', string="Meaurement Type")
    measurement_unit = fields.Many2one('uom.uom', string="Measurement Unit", default=_default_measurement_unit)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_fields_for_order_line(self):
        fields = super()._get_fields_for_order_line()
        fields.extend(['measurement_ids', 'measurement_unit'])
        return fields

    @api.model
    def _export_for_ui(self, order):
        result = super()._export_for_ui(order)
        order_lines_details = [{
            'uom_id': line.uom_id.id if line.uom_id else None,
            'uom_name': line.uom_id.name if line.uom_id else '',
            'measurement_ids': [m.id for m in line.measurement_ids] if line.measurement_ids else [],
            'measurement_unit_id': line.measurement_unit.id if line.measurement_unit else None,
            'measurement_unit_name': line.measurement_unit.name if line.measurement_unit else ''
        } for line in order.order_line_ids]
        result['order_lines_details'] = order_lines_details
        return result

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    measurement_ids = fields.Many2many('measurement.measurement', string='Measurement')
    measurement_unit = fields.Many2one('uom.uom', string="Measurement Unit")

    def _export_for_ui(self):
        result = super()._export_for_ui()
        result.update({
            'uom_id': self.uom_id.id if self.uom_id else False,
            'uom_name': self.uom_id.name if self.uom_id else '',
            'measurement_ids': self.measurement_ids.ids or [],
            'measurement_unit_id': self.measurement_unit.id if self.measurement_unit else False,
            'measurement_unit_name': self.measurement_unit.name if self.measurement_unit else ''
        })
        return result
    
    @api.model
    def _order_line_fields(self, line, session_id=None):
        fields_return = super()._order_line_fields(line, session_id=session_id)
        fields_return[2].update({
            'measurement_ids': line[2].get('measurement_ids', ''),
            'measurement_unit': line[2].get('measurement_unit', ''),
            'uom_id': line[2].get('uom_id') or self.get_product_uom(line[2].get('product_id')).id
        })
        return fields_return

    def get_product_uom(self, product_id):
        product = self.env['product.product'].browse(product_id)
        return product.uom_id

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        models = super()._pos_ui_models_to_load()
        additional_models = [
            'uom.uom',
            'uom.category',
            'measurement.type',
            'measurement.measurement.category',
            'measurement.measurement',
            'res.config.settings',
        ]
        for model in additional_models:
            if model not in models:
                models.append(model)
        return models

    def _loader_params_pos_category(self):
        result = super()._loader_params_pos_category()
        result['search_params']['fields'].extend([
            'measurement_unit',
            'measurement_type_ids',
        ])
        return result

    def _loader_params_measurement_measurement_category(self):
        return {
            'search_params': {
                'fields': [
                    'name',
                    'date',
                    'category_id',
                    'active',
                    'measurement_types',
                    'measurement_ids',
                    'measurement_unit',
                ],
            },
            'context': {'display_default_code': False},
        }

    def _get_pos_ui_measurement_measurement_category(self, params):
        return self.env['measurement.measurement.category'].with_context(**params['context']).search_read(**params['search_params'])

    def _loader_params_measurement_type(self):
        return {
            'search_params': {
                'fields': [
                    'name',
                    'active',
                    'sequence_number',
                    'measurement_cat_ids',
                    'pos_extra_price',
                    'currency_id',
                ],
            },
            'context': {'display_default_code': False},
        }

    def _get_pos_ui_measurement_type(self, params):
        return self.env['measurement.type'].with_context(**params['context']).search_read(**params['search_params'])

    def _loader_params_measurement_measurement(self):
        return {
            'search_params': {
                'fields': [
                    'name',
                    'date',
                    'active',
                    'sequence_number',
                    'partner_id',
                    'category_id',
                    'measurement_cat_ids',
                    'measurement',
                    'measurement_type',
                    'measurement_unit',
                    'pos_extra_price',
                    'currency_id',
                ],
            },
            'context': {'display_default_code': False},
        }

    def _get_pos_ui_measurement_measurement(self, params):
        return self.env['measurement.measurement'].with_context(**params['context']).search_read(**params['search_params'])

    def _get_pos_ui_product_template(self, params):
        return self.env['product.template'].search_read(**params['search_params'])

    def _loader_params_product_product(self):
        if hasattr(super(PosSession, self), '_loader_params_product_product'):
            result = super(PosSession, self)._loader_params_product_product()
        else:
            result = {'search_params': {'fields': []}}
        if 'fields' in result['search_params']:
            fields = result['search_params']['fields']
        else:
            fields = []
            result['search_params']['fields'] = fields
        fields.extend([
            'is_custom_product',
            'allow_measurements',
            'measurement_cat_ids',
        ])
        return result

    def _loader_params_product_uom_price(self):
        return {"search_params": {"fields": ['uom_id', 'qty', 'unit_price', 'price']}}

    def _get_pos_ui_product_uom_price(self, params):
        return self.env["product.uom.price"].search_read(**params["search_params"])

    def _loader_params_uom_category(self):
        return {"search_params": {"fields": ['name', 'is_custom_product']}}

    def _get_pos_ui_uom_category(self, params):
        return self.env["uom.category"].search_read(**params["search_params"])

    def _loader_params_res_partner(self):
        result = super()._loader_params_res_partner()
        result['search_params']['fields'].append('measurement_ids')
        return result

    def _loader_params_res_config_settings(self):
        return {
            'search_params': {
                'fields': [
                    'product_id',
                    'product_configure',
                    'allow_measurements',
                ],
            },
        }

    def _get_pos_ui_res_config_settings(self, params):
        return self.env['res.config.settings'].sudo().search_read(**params['search_params'])

class PosConfig(models.Model):
    _inherit = 'pos.config'

    product_id = fields.Many2one("product.product", string="Product", domain=[('available_in_pos', '=', True)])
    product_configure = fields.Boolean(string="Allow Product Configure", default=True)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_id = fields.Many2one(related='pos_config_id.product_id', readonly=False)
    product_configure = fields.Boolean(related='pos_config_id.product_configure', readonly=False)
    allow_measurements = fields.Boolean(string="Allow Measurements", config_parameter="pos_receipt_extend.allow_measurements")

class ResPartner(models.Model):
    _inherit = 'res.partner'

    measurement_ids = fields.One2many('measurement.measurement', 'partner_id', string='Measurements')

    @api.model
    def add_measurement(self, partner_id, measurement_values):
        partner = self.browse(partner_id)
        if not partner:
            raise ValidationError("Partner not found")

        for values in measurement_values:
            category_id = values.get('category_id')
            measurement_unit_id = values.get('measurement_unit')

            # Ensure category exists
            category = self.env['pos.category'].browse(category_id)
            if not category:
                raise ValidationError(f"No measurement category found for category ID {category_id}")

            # Ensure measurement unit exists
            measurement_unit = self.env['uom.uom'].browse(measurement_unit_id)
            if not measurement_unit:
                raise ValidationError(f"No measurement unit found for measurement unit ID {measurement_unit_id}")

            # Find existing measurement category or use the first found
            existing_category = self.env['measurement.measurement.category'].search([
                ('category_id', '=', category_id),
                ('measurement_unit', '=', measurement_unit_id),
            ], limit=1)

            if not existing_category:
                raise ValidationError(f"No measurement category found for category ID {category_id} and measurement unit ID {measurement_unit_id}")

            measurements = [
                {
                    'partner_id': partner_id,
                    'category_id': existing_category.id,
                    'measurement_type': m.get('measurement_type'),
                    'measurement': m.get('measurement'),
                    'measurement_unit': measurement_unit_id,
                }
                for m in values.get('measurement_ids', [])
            ]

            self.env['measurement.measurement'].create(measurements)

    def get_measurements(self):
        measurements = []
        for record in self:
            measurement_lines = self.env['measurement.measurement'].search([('partner_id', '=', record.id)])
            for line in measurement_lines:
                measurements.append({
                    'id': line.id,
                    'date': line.date,
                    'category': line.category_id.name,
                    'unit': line.measurement_unit.name,
                    'values': [{'id': line.id, 'name': line.measurement_type.name, 'value': line.measurement}]
                })
        return measurements

    @api.model
    def delete_measurement(self, measurement_ids):
        try:
            measurements = self.env['measurement.measurement'].browse(measurement_ids)
            if measurements:
                measurements.unlink()
                return {'success': True, 'message': 'Measurements deleted successfully'}
            else:
                return {'success': False, 'message': 'Measurements not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    measurement_ids = fields.Many2many('measurement.measurement', 'sale_order_measurement_rel', 'sale_order_id', 'measurement_id', string='Measurements')

    @api.model
    def add_measurement(self, sale_order_id, measurement_values):
        sale_order = self.browse(sale_order_id)
        if not sale_order:
            raise ValidationError("Sale Order not found")

        for values in measurement_values:
            category_id = values.get('category_id')
            measurement_unit_id = values.get('measurement_unit')

            # Ensure category exists
            category = self.env['pos.category'].browse(category_id)
            if not category:
                raise ValidationError(f"No measurement category found for category ID {category_id}")

            # Ensure measurement unit exists
            measurement_unit = self.env['uom.uom'].browse(measurement_unit_id)
            if not measurement_unit:
                raise ValidationError(f"No measurement unit found for measurement unit ID {measurement_unit_id}")

            # Find existing measurement category or use the first found
            existing_category = self.env['measurement.measurement.category'].search([
                ('category_id', '=', category_id),
                ('measurement_unit', '=', measurement_unit_id),
                ('sale_order_id', '=', sale_order_id)
            ], limit=1)

            if not existing_category:
                raise ValidationError(f"No measurement category found for category ID {category_id} and measurement unit ID {measurement_unit_id}")

            measurements = [
                {
                    'sale_order_id': sale_order_id,
                    'category_id': existing_category.id,
                    'measurement_type': m.get('measurement_type'),
                    'measurement': m.get('measurement'),
                    'measurement_unit': measurement_unit_id,
                }
                for m in values.get('measurement_ids', [])
            ]

            self.env['measurement.measurement'].create(measurements)