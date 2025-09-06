from odoo import api, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_configurator_context(self, product_id, **kwargs):
        ctx = super()._prepare_configurator_context(product_id, **kwargs)
        product = self.env['product.product'].browse(product_id)
        tmpl = product.product_tmpl_id
        if tmpl.laterality_enabled:
            ctx = dict(ctx or {})
            ctx.update({
                'laterality_enabled': True,
                'laterality_default': tmpl.laterality_default,
                'bilateral_default_type': tmpl.bilateral_default_type,
            })
        return ctx
