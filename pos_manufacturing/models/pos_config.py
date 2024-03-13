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
    set_tip_after_payment = fields.Boolean('Set Tip After Payment', help="Adjust the amount authorized by payment terminals to add a tip after the customers left or at the end of the day.")
    iface_tax_included = fields.Selection([('subtotal', 'Tax-Excluded Price'), ('total', 'Tax-Included Price')], string="Tax Display", default='subtotal', required=True)
    iface_splitbill = fields.Boolean(string='Bill Splitting', help='Enables Bill Splitting in the Point of Sale.')
    iface_printbill = fields.Boolean(string='Bill Printing', help='Allows to print the Bill before payment.')
    iface_orderline_notes = fields.Boolean(string='Internal Notes', help='Allow custom Internal notes on Orderlines.', default=True)
    floor_ids = fields.Many2many('manufacturing.floor', string='Manufacturing Floors', help='The manufacturing floors served by this point of sale.')
    module_pos_restaurant = fields.Boolean("Restaurant", default=False)
    # module_pos_manufacturing = fields.Boolean("Manufacturing")
    module_pos_manufacturing = fields.Boolean("Manufacturing", default=True)
    module_pos_manufacturing_appointment = fields.Boolean("Table Booking")

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

    def get_tables_order_count_and_printing_changes(self):
        self.ensure_one()
        tables = self.env['manufacturing.table'].search([('floor_id.pos_config_ids', '=', self.id)])
        domain = [('state', '=', 'draft'), ('table_id', 'in', tables.ids)]

        order_stats = self.env['pos.order']._read_group(domain, ['table_id'], ['__count'])
        linked_orderlines = self.env['pos.order.line'].search([('order_id.state', '=', 'draft'), ('order_id.table_id', 'in', tables.ids)])
        orders_map = {table.id: count for table, count in order_stats}
        changes_map = defaultdict(lambda: 0)
        skip_changes_map = defaultdict(lambda: 0)

        for line in linked_orderlines:
            # For the moment, as this feature is not compatible with pos_self_order,
            # we ignore last_order_preparation_change when it is set to false.
            # In future, pos_self_order will send the various changes to the order.
            if not line.order_id.last_order_preparation_change:
                line.order_id.last_order_preparation_change = '{}'

            last_order_preparation_change = json.loads(line.order_id.last_order_preparation_change)
            prep_change = {}
            for line_uuid in last_order_preparation_change:
                prep_change[last_order_preparation_change[line_uuid]['line_uuid']] = last_order_preparation_change[line_uuid]
            quantity_changed = 0
            if line.uuid in prep_change:
                quantity_changed = line.qty - prep_change[line.uuid]['quantity']
            else:
                quantity_changed = line.qty

            if line.skip_change:
                skip_changes_map[line.order_id.table_id.id] += quantity_changed
            else:
                changes_map[line.order_id.table_id.id] += quantity_changed

        result = []
        for table in tables:
            result.append({'id': table.id, 'orders': orders_map.get(table.id, 0), 'changes': changes_map.get(table.id, 0), 'skip_changes': skip_changes_map.get(table.id, 0)})
        return result

    def _get_forbidden_change_fields(self):
        forbidden_keys = super(PosConfig, self)._get_forbidden_change_fields()
        forbidden_keys.append('floor_ids')
        return forbidden_keys

    def _set_tips_after_payment_if_country_custom(self):
        self.ensure_one()
        company = self.company_id or self.env.company or self.env['res.company']._get_main_company()
        if company and company.country_id and company.country_id.code == 'US':
            self.update({
                'iface_tipproduct': True,
                'set_tip_after_payment': True,
            })

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            is_manufacturing = 'module_pos_manufacturing' not in vals or vals['module_pos_manufacturing']
            if is_manufacturing and 'iface_splitbill' not in vals:
                vals['iface_splitbill'] = True
            if not is_manufacturing or not vals.get('iface_tipproduct', False):
                vals['set_tip_after_payment'] = False
        pos_configs = super().create(vals_list)
        for config in pos_configs:
            if config.module_pos_manufacturing:
                self._setup_default_floor(config)
        return pos_configs

    def write(self, vals):
        if ('module_pos_manufacturing' in vals and vals['module_pos_manufacturing'] is False):
            vals['floor_ids'] = [(5, 0, 0)]

        if ('module_pos_manufacturing' in vals and not vals['module_pos_manufacturing']) or ('iface_tipproduct' in vals and not vals['iface_tipproduct']):
            vals['set_tip_after_payment'] = False

        if ('module_pos_manufacturing' in vals and vals['module_pos_manufacturing']):
            self._setup_default_floor(self)

        return super().write(vals)

    @api.model
    def post_install_pos_localisation(self, companies=False):
        self = self.sudo()
        if not companies:
            companies = self.env['res.company'].search([])
        super(PosConfig, self).post_install_pos_localisation(companies)
        for company in companies.filtered('chart_template'):
            pos_configs = self.search([
                *self.env['account.journal']._check_company_domain(company),
                ('module_pos_manufacturing', '=', True),
            ])
            if not pos_configs:
                pos_configs = self.env['pos.config'].with_company(company).create({
                'name': _('Bar'),
                'company_id': company.id,
                'module_pos_manufacturing': True,
                'iface_splitbill': True,
                'iface_printbill': True,
                'iface_orderline_notes': True,

            })
            pos_configs.setup_defaults(company)

    def setup_defaults(self, company):
        main_manufacturing = self.env.ref('pos_manufacturing.pos_config_main_manufacturing', raise_if_not_found=False)
        main_manufacturing_is_present = main_manufacturing and self.filtered(lambda cfg: cfg.id == main_manufacturing.id)
        if main_manufacturing_is_present:
            non_main_manufacturing_configs = self - main_manufacturing
            non_main_manufacturing_configs.assign_payment_journals(company)
            main_manufacturing._setup_main_manufacturing_defaults()
            self.generate_pos_journal(company)
            self.setup_invoice_journal(company)
        else:
            super().setup_defaults(company)

    def _setup_main_manufacturing_defaults(self):
        self.ensure_one()
        self._set_tips_after_payment_if_country_custom()
        self._link_same_non_cash_payment_methods_if_exists('point_of_sale.pos_config_main')
        self._ensure_cash_payment_method('MRCSH', _('Cash Manufacturing'))

    def _setup_default_floor(self, pos_config):
        if not pos_config.floor_ids:
            main_floor = self.env['manufacturing.floor'].create({
                'name': pos_config.company_id.name,
                'pos_config_ids': [(4, pos_config.id)],
            })
            self.env['manufacturing.table'].create({
                'name': '1',
                'floor_id': main_floor.id,
                'seats': 1,
                'position_h': 100,
                'position_v': 100,
                'width': 100,
                'height': 100,
            })
