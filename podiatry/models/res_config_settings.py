from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_podiatry_product_configurator = fields.Boolean(string="Custom Product Configurator")
    
    # show_product_image_line_item = fields.Boolean(string="Show Product Image", default=False)

    # @api.model
    # def set_values(self):
    #     self.env['ir.config_parameter'].sudo().set_param('podiatry.show_product_image_line_item',
    #                                                      self.show_product_image_line_item)
    #     res = super(ResConfigSettings, self).set_values()
    #     return res

    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     param = self.env['ir.config_parameter'].sudo().get_param(
    #         'podiatry.show_product_image_line_item',
    #         self.show_product_image_line_item)
    #     res.update(
    #         show_product_image_line_item=param
    #     )
    #     return res
