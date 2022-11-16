from odoo import models, fields, api


class ProductCustomize(models.Model):
    _inherit = 'product.product'
    amazon_progress = fields.Float('Amazon progress', compute='_compute_amazon_progress')
    ebay_progress = fields.Float('Ebay progress', compute='_compute_ebay_progress')
    lt_progress = fields.Float('LT progress', compute='_compute_lt_progress')
    lv_progress = fields.Float('LV progress', compute='_compute_lv_progress')
    ee_progress = fields.Float('EE progress', compute='_compute_ee_progress')

    def _cal_progress(self, att_list):
        add_proc = 100 / len(att_list)
        progress = 0
        for att in att_list:
            if getattr(self, att): progress += add_proc
        return round(progress, 0)

    @api.depends('lst_price', 'image_1920', 'uom_id', 'weight')
    def _compute_amazon_progress(self):
        amazon_field_list = ['lst_price', 'image_1920', 'uom_id', 'weight']
        for record in self:
            progress = record._cal_progress(amazon_field_list)
            setattr(record, 'amazon_progress', progress)

    @api.depends('lst_price', 'image_1920', 'allow_out_of_stock_order', 'product_template_variant_value_ids')
    def _compute_ebay_progress(self):
        ebay_field_list = ['lst_price', 'image_1920', 'allow_out_of_stock_order', 'product_template_variant_value_ids']
        for record in self:
            progress = record._cal_progress(ebay_field_list)
            setattr(record, 'ebay_progress', progress)

    @api.depends('lst_price', 'image_1920', 'uom_id', 'alternative_product_ids')
    def _compute_lt_progress(self):
        lt_field_list = ['lst_price', 'image_1920', 'uom_id', 'alternative_product_ids']
        for record in self:
            progress = record._cal_progress(lt_field_list)
            setattr(record, 'lt_progress', progress)

    @api.depends('lst_price', 'image_1920', 'volume', 'weight')
    def _compute_lv_progress(self):
        lv_field_list = ['lst_price', 'image_1920', 'volume', 'weight']
        for record in self:
            progress = record._cal_progress(lv_field_list)
            setattr(record, 'lv_progress', progress)

    @api.depends('lst_price', 'image_1920', 'volume', 'weight', 'accessory_product_ids')
    def _compute_ee_progress(self):
        ee_field_list = ['lst_price', 'image_1920', 'volume', 'weight', 'accessory_product_ids']
        for record in self:
            progress = record._cal_progress(ee_field_list)
            setattr(record, 'ee_progress', progress)

