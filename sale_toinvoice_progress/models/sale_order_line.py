# -*- coding: utf-8 -*-
# Copyright© 2016-2017 ICTSTUDIO <http://www.ictstudio.eu>
# License: AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced')
    def _compute_invoicing_progress(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('sale', 'done'):
                line.invoicing_progress = 0.0
            elif not float_is_zero(line.product_uom_qty, precision_digits=precision) and not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                if float_compare(line.product_uom_qty, line.qty_to_invoice, precision_digits=precision) >= 0:
                    line.invoicing_progress = 100 * (line.qty_to_invoice / line.product_uom_qty)
                else:
                    line.invoicing_progress = 0.0
            else:
                line.invoicing_progress = 0.0

    invoicing_progress = fields.Float(
        string='To Invoice',
        compute='_compute_invoicing_progress',
        store=True, readonly=True
    )
