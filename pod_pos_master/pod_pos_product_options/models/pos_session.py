# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        result = super(PosSessionInherit,self)._loader_params_product_product()
        result['search_params']['fields'].extend(['pod_option_ids','pod_is_global_option','pod_option_group_ids'])
        return result
    
    def _loader_params_pos_category(self):
        result = super(PosSessionInherit,self)._loader_params_pos_category()
        result['search_params']['fields'].append('pod_product_option_ids')
        return result