# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.tools import format_amount


class PrescriptionOrder(models.Model):
    """Inherited the model for adding the dashboard values"""
    _inherit = 'prescription.order'

    @api.model
    def get_dashboard_values(self):
        """This method returns values to the dashboard in prescription order views."""
        result = {
            'total_orders': 0,
            'draft_orders': 0,
            'prescription_orders': 0,
            'my_orders': 0,
            'my_draft_orders': 0,
            'my_prescription_orders': 0,
            'total_prescription_amount': 0,
            'total_draft_amount': 0,
        }
        prescription_order = self.env['prescription.order']
        user = self.env.user
        result['total_orders'] = prescription_order.search_count([])
        result['draft_orders'] = prescription_order.search_count(
            [('state', 'in', ['draft', 'sent'])])
        result['prescription_orders'] = prescription_order.search_count(
            [('state', 'in', ['prescription', 'done'])])
        result['my_orders'] = prescription_order.search_count(
            [('user_id', '=', user.id)])
        result['my_draft_orders'] = prescription_order.search_count(
            [('user_id', '=', user.id), ('state', 'in', ['draft', 'sent'])])
        result['my_prescription_orders'] = prescription_order.search_count(
            [('user_id', '=', user.id), ('state', 'in', ['prescription', 'done'])])
        order_sum = """select sum(amount_total) from prescription_order where state 
        in ('prescription', 'done')"""
        self._cr.execute(order_sum)
        res = self.env.cr.fetchone()
        result['total_prescription_amount'] = format_amount(self.env, res[0] or 0,
                                                    self.env.company.currency_id)
        draft_sum = """select sum(amount_total) from prescription_order where state 
        in ('draft', 'sent')"""
        self._cr.execute(draft_sum)
        res = self.env.cr.fetchone()
        result['total_draft_amount'] = format_amount(self.env, res[0] or 0,
                                                     self.env.company.currency_id)
        return result
