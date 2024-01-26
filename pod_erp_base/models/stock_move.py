# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    # Overloading this method to add custom functionality
    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()

        # Setting the value or pod_order_uuid if it's from sale order
        model = dict(self.env.context).get("params") and dict(self.env.context).get("params")["model"] or False

        if model and model == 'sale.order' and self.group_id.sale_id.pod_order_uuid:
            res.update({'pod_order_uuid': self.group_id.sale_id.pod_order_uuid})
    
        return res
