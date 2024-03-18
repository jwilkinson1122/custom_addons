# -*- coding: utf-8 -*-


from pkg_resources import require
from odoo import models, fields, api, _

class PodOptionGroup(models.Model):
    _name = 'pod.option.group'
    _description = "Define Options products"

    name = fields.Char(string="Name", required=True)
    options_ids = fields.Many2many('product.product', string="Options", domain="[('available_in_pos', '=', True)]")

class MassUpdateOptions(models.TransientModel):
    _name = 'pod.mass.update.options'
    _description= 'mass update option'

    pod_option_group_ids = fields.Many2many('pod.option.group', 'massupdate_option_group', string="Options Groups")
    pod_option_product_ids = fields.Many2many('product.product', string="Options", domain="[('available_in_pos', '=', True)]")

    @api.onchange('pod_option_group_ids')
    def _onchange_pod_option_group_ids(self):
            option_groups = self.env['pod.option.group'].browse(self.pod_option_group_ids.ids)
            option_ids = []
            if option_groups:
                for option_groupid in option_groups: 
                    for tid in option_groupid.options_ids:
                        option_ids.append(tid.id)
            self.update({'pod_option_product_ids':[(6,0,option_ids)] })

    def updateOptions(self):
        #update selected product options
        products = self.env['product.product'].browse(self._context.get('active_ids'))
        for product in products:
            product.pod_option_group_ids = self.pod_option_group_ids
            product.pod_option_ids = self.pod_option_product_ids
