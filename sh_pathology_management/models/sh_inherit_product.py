# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class Product_General(models.Model):
    _inherit = 'product.product'

    sh_patho_report_delivery_time = fields.Integer(
        string="Report Delivery Time")
    sh_patho_report_delivery_type = fields.Selection(
        [('day', 'Day'), ('week', 'Week')], string="With In")
    sh_patho_pre_info_id = fields.Many2one(
        'sh.lab.test.pre.info', string="Pre-information")
    sh_patho_sample_type_id = fields.Many2one(
        'sh.lab.test.sample.type', string="Sample Type")
    sh_patho_test_parameter_ids = fields.Many2many('sh.lab.test.parameter')
    sh_patho_is_lab_test_product = fields.Boolean(string="Lab Test Product")
    sh_patho_product_total_tests = fields.Integer(
        compute="get_total_of_product_tests")

    def get_total_of_product_tests(self):
        for rec in self:
            lines = self.env['sh.patho.request.line'].search(
                [('product_id.name', '=', rec.name)])
            product_total_tests = len(lines.ids)
            self.sh_patho_product_total_tests = product_total_tests

    def blank_method(self):
        pass
