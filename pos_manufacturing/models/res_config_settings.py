# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # pos_config_id = fields.Many2one('pos.config', string="Point of Sale", default=lambda self: self._default_pos_config())
    pos_a4_receipt = fields.Boolean(related='pos_config_id.a4_receipt', readonly=False)
    pos_a4_receipt_as_default = fields.Boolean(related='pos_config_id.a4_receipt_as_default', readonly=False)
    pos_tracking = fields.Selection(related='pos_config_id.tracking', readonly=False)
    pos_show_taxes = fields.Boolean(related='pos_config_id.show_taxes', readonly=False)
    pos_create_draft_sale_order = fields.Boolean(related="pos_config_id.create_draft_sale_order", readonly=False)
    pos_create_confirmed_sale_order = fields.Boolean(related="pos_config_id.create_confirmed_sale_order", readonly=False)
    pos_create_delivered_sale_order = fields.Boolean(related="pos_config_id.create_delivered_sale_order", readonly=False)
    pos_create_invoiced_sale_order = fields.Boolean(related="pos_config_id.create_invoiced_sale_order", readonly=False)
    pos_allow_reorder = fields.Boolean(related="pos_config_id.allow_reorder", readonly=False)
    pos_configure_product = fields.Boolean(related='pos_config_id.product_configure', readonly=False)
    pos_module_pos_restaurant = fields.Boolean(related='pos_config_id.module_pos_restaurant', readonly=False)
    pos_module_pos_manufacturing = fields.Boolean(related='pos_config_id.module_pos_manufacturing', readonly=False)
    pos_is_order_printer = fields.Boolean(compute='_compute_pos_printer', store=True, readonly=False)
    pos_printer_ids = fields.Many2many(related='pos_config_id.printer_ids', readonly=False)
    pos_floor_ids = fields.Many2many(related='pos_config_id.floor_ids', readonly=False)
    pos_iface_orderline_notes = fields.Boolean(compute='_compute_pos_module_pos_manufacturing', store=True, readonly=False)
    pos_iface_printbill = fields.Boolean(compute='_compute_pos_module_pos_manufacturing', store=True, readonly=False)
    pos_iface_splitbill = fields.Boolean(compute='_compute_pos_module_pos_manufacturing', store=True, readonly=False)
    pos_iface_tax_included = fields.Selection(related='pos_config_id.iface_tax_included', readonly=False)
    pos_set_tip_after_payment = fields.Boolean(compute='_compute_pos_set_tip_after_payment', store=True, readonly=False)
    pos_module_pos_manufacturing_appointment = fields.Boolean(related="pos_config_id.module_pos_manufacturing_appointment", readonly=False)

    @api.depends('pos_module_pos_manufacturing', 'pos_config_id')
    def _compute_pos_module_pos_manufacturing(self):
        for res_config in self:
            if not res_config.pos_module_pos_manufacturing:
                res_config.update({
                    'pos_iface_orderline_notes': False,
                    'pos_iface_printbill': False,
                    'pos_iface_splitbill': False,
                })
            else:
                res_config.update({
                    'pos_iface_orderline_notes': res_config.pos_config_id.iface_orderline_notes,
                    'pos_iface_printbill': res_config.pos_config_id.iface_printbill,
                    'pos_iface_splitbill': res_config.pos_config_id.iface_splitbill,
                })

    @api.depends('pos_iface_tipproduct', 'pos_config_id')
    def _compute_pos_set_tip_after_payment(self):
        for res_config in self:
            if res_config.pos_iface_tipproduct:
                res_config.pos_set_tip_after_payment = res_config.pos_config_id.set_tip_after_payment
            else:
                res_config.pos_set_tip_after_payment = False


    @api.depends('pos_module_pos_manufacturing', 'pos_config_id')
    def _compute_pos_printer(self):
        for res_config in self:
            res_config.update({
                'pos_is_order_printer': res_config.pos_config_id.is_order_printer,
            })