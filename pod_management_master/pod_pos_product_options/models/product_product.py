# -*- coding: utf-8 -*-

 
from asyncio import constants
from cmath import cos
from odoo import models, fields, api, _

class PosProductInherit(models.Model):
    _inherit = "product.product"

    pod_is_global_option = fields.Boolean(string="Global Option")
    pod_option_ids = fields.Many2many('product.product', 'product_pos_options', 'name', string="Options", domain="[('available_in_pos', '=', True)]")
    pod_option_group_ids = fields.Many2many('pod.option.group', 'product_option_group', string="Option Group")

    @api.onchange('pod_option_group_ids')
    def _onchange_pod_option_group_ids(self):
            option_groups = self.env['pod.option.group'].browse(self.pod_option_group_ids.ids)
            option_ids = []
            if option_groups:
                for option_groupid in option_groups: 
                    for tid in option_groupid.option_ids: 
                        option_ids.append(tid.id)
            self.update({'pod_option_ids':[(6,0,option_ids)] })
                
    def action_update_options(self): 
        return {
            'name': 'Update Options',
            'res_model': 'pod.mass.update.options',
            'view_mode': 'form',
            'context': {
                'active_model': 'product.product',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
