# -*- coding: UTF-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    quantity_counts = fields.Char(string='Quantity Counts', compute='_compute_quantity_counts', store=False)

    @api.depends('move_lines')
    def _compute_quantity_counts(self):
        for rec in self:
            results = []
            for line in rec.move_lines:
                if line.product_qty>0:
                    if line.secondary_uom_enabled:
                        fres = list(filter(lambda x: x['uom_name'].lower()==line.secondary_uom_name.lower(), results))
                        if fres:
                            fres[0]['qty'] = fres[0]['qty'] + line.secondary_qty
                        else:
                            results.append({
                                'uom_name': line.secondary_uom_name,
                                'qty': line.secondary_qty
                                })
                    else:
                        fres = list(filter(lambda x: x['uom_name'].lower()==line.product_uom.name.lower(), results))
                        if fres:
                            fres[0]['qty'] = fres[0]['qty'] + line.product_qty
                        else:
                            results.append({
                                'uom_name': line.product_uom.name,
                                'qty': line.product_qty
                                })

            resultString = []
            for line in results:
                if line['qty'] > 1:
                    resultString.append(str(line['qty']) + " " + line['uom_name'] + "s")
                elif line['qty'] > 0:
                    resultString.append(str(line['qty']) + " " + line['uom_name'])
            
            if resultString:
                rec.quantity_counts = 'Quantity Counts: ' + ('; '.join(resultString))
            else:
                rec.quantity_counts = ''
