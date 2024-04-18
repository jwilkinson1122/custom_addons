from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit ='pos.order.line'

    measurment_ids = fields.Many2many('measurment.measurment', string='Measurement')
    measurment_unit = fields.Many2one('uom.uom', string="Measurement Unit") 

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_fields_for_order_line(self):
        fields = super(PosOrder, self)._get_fields_for_order_line()
        fields.extend(['measurment_ids', 'measurment_unit',])
        return fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_tailor_product = fields.Boolean(string="Is Tailor Product")
    # is_delivery_product = fields.Boolean(string="Is Delivery Product")

class ResPartner(models.Model):
    _inherit = 'res.partner'

    measurment_ids = fields.One2many('measurment.measurment.category', 'partner_id', 'Measurment')

    def add_measurment_category(self, measurment_values):
        data_dictonary = measurment_values
        mmc_object = self.env['measurment.measurment.category']
        mm_object = self.env['measurment.measurment']
        if data_dictonary:
            measurment_cat_id = mmc_object.create({
                'date': data_dictonary.get('date'),
                'partner_id': self.id,
                'category_id': data_dictonary.get('category_id'),
                'measurment_unit': int(data_dictonary.get('measurment_unit'))
                })
            if measurment_cat_id:
                for measurment in data_dictonary.get('measurment_ids'):
                    mm_object.create({
                        'measurment_cat_id': measurment_cat_id.id,
                        'measurment_type': measurment.get('measurment_type'),
                        'measurment': measurment.get('measurment_value')
                        })

class MeasurmentCategory(models.Model):
    _name = "measurment.measurment.category"

    date = fields.Date('Date')
    partner_id = fields.Many2one('res.partner', string='Partner',  required=True)
    category_id = fields.Many2one('pos.category', string='Category',  required=True)
    measurment_ids = fields.One2many('measurment.measurment', 'measurment_cat_id', 'Measurments')
    measurment_unit = fields.Many2one('uom.uom', string='Measurement Unit',  required=True)

class Measurment(models.Model):
    _name = 'measurment.measurment'
    _description = 'Measurment'
    _rec_name = 'name'

    name = fields.Char(compute="_compute_measurment_name")
    measurment_cat_id = fields.Many2one('measurment.measurment.category', string='Measurment Category',  required=True, ondelete='cascade')
    measurment = fields.Char('Measurment')
    measurment_type = fields.Many2one('measurment.type', string='Measurment Type', required=True)

    @api.depends('measurment_type', 'measurment')
    def _compute_measurment_name(self):
        for rec in self:
            if rec.measurment_type and rec.measurment:
                rec.name = rec.measurment_type.name + ': ' + rec.measurment
            else:
                rec.name = False

class MeasurmentType(models.Model):
    _name = "measurment.type"

    name = fields.Char(string="Name")

class PosCategory(models.Model):
    _inherit = 'pos.category'

    @api.model
    def _default_measurment_unit(self):
        measurment_unit = self.env.ref('uom.product_uom_inch', False)
        if measurment_unit:
            return measurment_unit.id
        return False

    measurment_type_ids = fields.Many2many('measurment.type', string="Measurment Type")
    measurment_unit = fields.Many2one('uom.uom', string="Measurment Unit", default=_default_measurment_unit)

class PosSesion(models.Model):
    _inherit = "pos.session"

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append('measurment.type')
        result.append('measurment.measurment.category')
        result.append('measurment.measurment')
        return result


    def _loader_params_res_partner(self):
        result = super(PosSesion, self)._loader_params_res_partner()
        result['search_params']['fields'].append('measurment_ids')
        return result

    def _loader_params_product_template(self):
        result = super(PosSesion, self)._loader_params_product_template()
        result['search_params']['fields'].append('is_tailor_product')
        # result['search_params']['fields'].append('is_delivery_product')
        return result

    def _loader_params_product_product(self):
        result = super(PosSesion, self)._loader_params_product_product()
        result['search_params']['fields'].append('is_tailor_product')
        # result['search_params']['fields'].append('is_delivery_product')
        return result

    def _loader_params_pos_category(self):
        result = super(PosSesion, self)._loader_params_pos_category()
        result['search_params']['fields'].append('measurment_unit')
        result['search_params']['fields'].append('measurment_type_ids')
        return result

    def _get_pos_ui_measurment_type(self, params):
        return self.env['measurment.type'].with_context(**params['context']).search_read(**params['search_params'])

    def _loader_params_measurment_type(self):
        return {
            'search_params': {'fields': ['name',],},
            'context': {'display_default_code': False},
        }

    def _get_pos_ui_measurment_measurment_category(self, params):
        return self.env['measurment.measurment.category'].with_context(**params['context']).search_read(**params['search_params'])
    
    def _loader_params_measurment_measurment_category(self):
        return {
            'search_params': {
                'fields': [
                    'date',
                    'partner_id',
                    'category_id',
                    'measurment_unit',
                    'measurment_ids']
                    ,},
            'context': {'display_default_code': False},
        }

    def _get_pos_ui_measurment_measurment(self, params):
        return self.env['measurment.measurment'].with_context(**params['context']).search_read(**params['search_params'])
    
    def _loader_params_measurment_measurment(self):
        return {
            'search_params': {
                'fields': [
                    'name',
                    'measurment',
                    'measurment_type',
                    'measurment_cat_id',]
                    ,},
            'context': {'display_default_code': False},
        }