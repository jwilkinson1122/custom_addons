import logging
import base64
from random import randint
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import file_open

_logger = logging.getLogger(__name__)

class PosOrderCustomizationGroup(models.Model):
    _name = 'pos.order.customization.group'
    _description = "Order Customization Group"

    name = fields.Char('Name', required=True)
    customizations = fields.Many2many('pos.order.customization', string='Customizations')
    active = fields.Boolean('Active', default=1)
    product_ids = fields.Many2many('product.template', string="Products")

    @api.constrains('customizations')
    def validate_customizations_count(self):
        if len(self.customizations) == 0:
            raise ValidationError("Please add at least one customization in the customization group")

class PosOrderCustomization(models.Model):
    _name = 'pos.order.customization'
    _description = "Order Customization"
    _order = "sequence_number desc"

    name = fields.Text('Customization', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence_number = fields.Integer('Sequence Number')

    display_type = fields.Selection(
        selection=[
            ('radio', 'Radio'),
            ('pills', 'Pills'),
            ('select', 'Select'),
            ('color', 'Color'),
            ('multi', 'Multi-checkbox (option)'),
        ],
        default='radio',
        required=True)
    
    sequence = fields.Integer(string="Sequence", help="Determine the display order", index=True)

    value_ids = fields.One2many(
        comodel_name='pos.order.customization.value',
        inverse_name='customization_id',
        string="Values", copy=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id.id)
    pos_extra_price = fields.Float('Extra Price', default=0)
    
    customization_groups = fields.Many2many('pos.order.customization.group', string='Available In Customization Groups')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence_number') == False:
                vals['sequence_number'] = self.env['ir.sequence'].next_by_code('pos.order.customization')
        return super(PosOrderCustomization, self).create(vals_list)

class PosOrderCustomizationValue(models.Model):
    _name = 'pos.order.customization.value'
    _description = "POS Order Customization Value"
    _order = 'customization_id, sequence, id'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Value", required=True, translate=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string="Sequence", help="Determine the display order", index=True)
    customization_id = fields.Many2one(
        comodel_name='pos.order.customization',
        string="Customization",
        ondelete='cascade',
        required=True,
        index=True)
    
    attribute_value_id = fields.Many2one(
        comodel_name='product.attribute.value',
        string="Product Attribute Value",
        ondelete='cascade',
        required=True,
        index=True)

    is_used_on_products = fields.Boolean(string="Used on Products", compute='_compute_is_used_on_products')
    pos_extra_price = fields.Float('Extra Price', default=0)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id.id)
    default_extra_price = fields.Float()
    is_custom = fields.Boolean(
        string="Is custom value",
        help="Allow users to input custom values for this customization value")
    html_color = fields.Char(
        string="Color",
        help="Set a specific HTML color index (e.g., #ff0000) for color customizations.")
    display_type = fields.Selection(related='customization_id.display_type')
    color = fields.Integer(string="Color Index", default=_get_default_color)
    image = fields.Image(
        string="Image",
        help="Upload an image used as the color of the customization value.",
        max_width=70,
        max_height=70,
    )

    @api.depends('customization_id')
    def _compute_is_used_on_products(self):
        """Compute if this customization value is used on any product."""
        for record in self:
            record.is_used_on_products = bool(record.customization_id.mapped('customization_groups.product_ids'))


    @api.constrains('pos_extra_price')
    def validate_extra_price(self):
        if self.pos_extra_price < 0:
            raise ValidationError("Extra Price cannot be less than zero.")

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    order_customizations = fields.Text('Extra Comments')

    @api.model
    def _order_line_fields(self, line, session_id=None):
        fields_return = super(PosOrderLine, self)._order_line_fields(line, session_id)
        fields_return[2].update({
            'order_customizations': line[2].get('order_customizations', '')
        })
        return fields_return

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        new_models = ['pos.order.customization.group', 'pos.order.customization', 'pos.order.customization.value']
        result.extend(new_models)
        return result

    def _loader_params_pos_order_customization_group(self):
        domain_list = []
        model_fields = []
        return {'search_params': {'domain': domain_list, 'fields': model_fields}}
    
    def _get_pos_ui_pos_order_customization_group(self, params):
        order_customization_groups = self.env['pos.order.customization.group'].search_read(**params['search_params'])
        return order_customization_groups
    
    def _loader_params_pos_order_customization(self):
        domain_list = []
        model_fields = []
        return {'search_params': {'domain': domain_list, 'fields': model_fields}}
    
    def _get_pos_ui_pos_order_customization(self, params):
        pos_order_customizations = self.env['pos.order.customization'].search_read(**params['search_params'])
        return pos_order_customizations

    def _loader_params_pos_order_customization_value(self):
        domain_list = []
        model_fields = []
        return {'search_params': {'domain': domain_list, 'fields': model_fields}}
    
    def _get_pos_ui_pos_order_customization_value(self, params):
        pos_order_customization_values = self.env['pos.order.customization.value'].search_read(**params['search_params'])
        return pos_order_customization_values

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['customization_group_ids'])
        return result




