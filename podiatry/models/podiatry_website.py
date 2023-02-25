from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        _logger.info('>>>>>>>')
        _logger.info(self.get_current_website().id)
        return ["|", "&"] + [("sale_ok", "=", True)] + [('is_web_pub', '=', True), ('type', '=', 'service')] + [('website_ids', 'in', [self.sudo().get_current_website().id] )] + [('website_ids', '=', False )] + self.get_current_website().website_domain()

    
    # def sale_product_domain(self):
    #     result = super(Website, self).sale_product_domain()
    #     result.extend([('is_web_pub', '=', True), ('type', '=', 'service')])
    #     return result

   