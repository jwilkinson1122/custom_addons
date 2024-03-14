# -*- coding: utf-8 -*-
# Copyright© 2016-2017 ICTSTUDIO <http://www.ictstudio.eu>
# License: AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('state', 'order_line.invoicing_progress')
    def _compute_invoicing_progress(self):
        # # Ignore the status of the deposit product
        # deposit_product_id = self.env['sale.advance.payment.inv']._default_product_id()
        # line_invoice_status = [line.invoice_status for line in order.order_line if line.product_id != deposit_product_id]
        #
        for order in self:
            tot_amount = order.amount_untaxed
            inv_progress = 0.0
            for line in order.order_line:
                if line.state in ('sale', 'done'):
                    if tot_amount:
                        inv_progress += line.invoicing_progress * (line.price_subtotal / tot_amount)
            if inv_progress < 0:
                inv_progress = -inv_progress
            if inv_progress and inv_progress < 3.0:
                inv_progress = 3.0
            order.invoicing_progress = inv_progress

    invoicing_progress = fields.Float(
        string='To Invoice',
        compute='_compute_invoicing_progress',
        store=True,
        readonly=True
    )