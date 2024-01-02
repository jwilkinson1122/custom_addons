# -*- coding: utf-8 -*-

from odoo import models


class ProductTemplate(models.Model):
    """Extends the product.template model to generate QR codes for all
    related product variants."""
    _inherit = 'product.template'

    def generate_qr(self):
        """Generate QR codes for all product variants associated with the
        product template."""
        product = self.env['product.product'].search(
            [('product_tmpl_id', '=', self.id), ])
        for rec in product:
            rec.generate_qr()
        return self.env.ref('pod_qrcode.print_qr2').report_action(
            self, data={'data': self.id, 'type': 'all'})
