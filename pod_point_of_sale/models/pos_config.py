# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import json
from collections import defaultdict


class PosConfig(models.Model):
    _inherit = "pos.config"

    create_mrp_order = fields.Boolean("Create MRP Order", help="Allow MRP order creation in PoS", default=True)
    mrp_order_done = fields.Boolean("MRP Order Done", help="Allow Done MRP orders in PoS", default=True)
    allow_reorder = fields.Boolean(default=True)
    product_configure = fields.Boolean(string="Allow Product Configure", default=True)
    a4_receipt = fields.Boolean("A4 Receipt", default=True)
    a4_receipt_as_default = fields.Boolean(string='Default', default=True)
    tracking = fields.Selection([('barcode', 'Barcode'), ('qrcode', 'Qrcode')], string="Tracking", default='qrcode')
    show_taxes = fields.Boolean("Taxes", default=False)
    iface_tax_included = fields.Selection([('subtotal', 'Tax-Excluded Price'), ('total', 'Tax-Included Price')], string="Tax Display", default='subtotal', required=True)
    module_pos_restaurant = fields.Boolean("Is a Bar/Restaurant", default=False)

    create_sale_order = fields.Boolean(
        string="Create Sale Orders",
        compute="_compute_create_sale_order",
        store=True,
    )

    create_draft_sale_order = fields.Boolean(
        string="Create Draft Sale Orders",
        default=True,
        help="If checked, the cashier will have the possibility to create"
        " a draft Sale Order, based on the current draft PoS Order.",
    )

    create_confirmed_sale_order = fields.Boolean(
        string="Create Confirmed Sale Orders",
        default=True,
        help="If checked, the cashier will have the possibility to create"
        " a confirmed Sale Order, based on the current draft PoS Order.",
    )

    create_delivered_sale_order = fields.Boolean(
        string="Create Delivered Sale Orders",
        default=True,
        help="If checked, the cashier will have the possibility to create"
        " a confirmed sale Order, based on the current draft PoS Order.\n"
        " the according picking will be marked as delivered. Only invoices"
        " process will be possible.",
    )

    create_invoiced_sale_order = fields.Boolean(
        string="Create Invoiced Sale Orders",
        default=True,
        help="If checked, the cashier will have the possibility to create"
        " a confirmed sale Order, based on the current draft PoS Order.\n"
        " the according picking will be marked as delivered.\n"
        " The Invoice will be generated and confirm.\n"
        " Only invoice payment process will be possible.",
    )

    @api.depends(
        "create_draft_sale_order",
        "create_confirmed_sale_order",
        "create_delivered_sale_order",
        "create_invoiced_sale_order",
    )
    def _compute_create_sale_order(self):
        for config in self:
            config.create_sale_order = any(
                [
                    config.create_draft_sale_order,
                    config.create_confirmed_sale_order,
                    config.create_delivered_sale_order,
                    config.create_invoiced_sale_order,
                ]
            )

    @api.onchange('a4_receipt')
    def _onchange_a4_receipt(self):
        if not self.a4_receipt:
            self.a4_receipt_as_default = False
            self.tracking = False