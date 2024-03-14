# -*- coding: utf-8 -*-


from odoo import models, fields, api, _

class PosOrderlineInherit(models.Model):
    _inherit = 'pos.order.line'

    pod_has_option = fields.Boolean(string="Has Option")
    pod_is_option = fields.Boolean(string="is Option")

    def _export_for_ui(self, orderline):
        result = super(PosOrderlineInherit, self)._export_for_ui(orderline)

        result['pod_has_option'] = orderline.pod_has_option,
        result['pod_is_option'] = orderline.pod_is_option,
        return result
        
class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    def _get_fields_for_order_line(self):
        fields = super(PosOrderInherit, self)._get_fields_for_order_line()
        fields.extend(['pod_has_option', 'pod_is_option'])
        
        return fields