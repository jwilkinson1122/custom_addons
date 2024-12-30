from odoo import api, fields, models

class IrCron(models.Model):
    _inherit = 'ir.cron'

    @api.model
    def _cron_product_price_update(self):
        product_price_updater = self.env['product.price.updater']
        product_price_updater.update_product_prices_cron()
