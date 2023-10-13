# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_pod_calendar = fields.Boolean(
        string="Prescriptions for Patients")
    module_pod_encounter = fields.Boolean(
        string="Encounters for Patients")
    module_pod_patient_tags = fields.Boolean(string="Tags for Patients")
    module_pod_phone_validation = fields.Boolean(
        string="Phone Number Validation for Patients")
    
    show_product_image_line_item = fields.Boolean(string="Show Product Image", default=False)

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('pod_order_management.show_product_image_line_item',
                                                         self.show_product_image_line_item)
        res = super(ResConfigSettings, self).set_values()
        return res

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo().get_param(
            'pod_order_management.show_product_image_line_item',
            self.show_product_image_line_item)
        res.update(
            show_product_image_line_item=param
        )
        return res
