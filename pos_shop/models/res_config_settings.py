# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_floor_ids = fields.Many2many(related='pos_config_id.floor_ids', readonly=False)
    pos_iface_orderline_notes = fields.Boolean(compute='_compute_pos_module_pos_shop', store=True, readonly=False)
    pos_iface_printinvoice = fields.Boolean(compute='_compute_pos_module_pos_shop', store=True, readonly=False)
    pos_iface_splitinvoice = fields.Boolean(compute='_compute_pos_module_pos_shop', store=True, readonly=False)
    pos_set_tip_after_payment = fields.Boolean(compute='_compute_pos_set_tip_after_payment', store=True, readonly=False)
    pos_module_pos_shop_appointment = fields.Boolean(related="pos_config_id.module_pos_shop_appointment", readonly=False)

    @api.depends('pos_module_pos_shop', 'pos_config_id')
    def _compute_pos_module_pos_shop(self):
        for res_config in self:
            if not res_config.pos_module_pos_shop:
                res_config.update({
                    'pos_iface_orderline_notes': False,
                    'pos_iface_printinvoice': False,
                    'pos_iface_splitinvoice': False,
                })
            else:
                res_config.update({
                    'pos_iface_orderline_notes': res_config.pos_config_id.iface_orderline_notes,
                    'pos_iface_printinvoice': res_config.pos_config_id.iface_printinvoice,
                    'pos_iface_splitinvoice': res_config.pos_config_id.iface_splitinvoice,
                })

    @api.depends('pos_iface_tipproduct', 'pos_config_id')
    def _compute_pos_set_tip_after_payment(self):
        for res_config in self:
            if res_config.pos_iface_tipproduct:
                res_config.pos_set_tip_after_payment = res_config.pos_config_id.set_tip_after_payment
            else:
                res_config.pos_set_tip_after_payment = False
