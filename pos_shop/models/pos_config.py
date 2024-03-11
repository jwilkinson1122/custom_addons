# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
import json
from collections import defaultdict


class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_splitinvoice = fields.Boolean(string='Invoice Splitting', help='Enables Invoice Splitting in the Point of Sale.')
    iface_printinvoice = fields.Boolean(string='Invoice Printing', help='Allows to print the Invoice before payment.')
    iface_orderline_notes = fields.Boolean(string='Internal Notes', help='Allow custom Internal notes on Orderlines.', default=True)
    floor_ids = fields.Many2many('shop.floor', string='Manufacturing Shop Floors', help='The manufacturing shop floors served by this point of sale.')
    set_tip_after_payment = fields.Boolean('Set Tip After Payment', help="Adjust the amount authorized by payment terminals to add a tip after the customers left or at the end of the day.")
    module_pos_shop = fields.Boolean(default=True)
    module_pos_shop_appointment = fields.Boolean("Section Booking")

    def get_sections_order_count_and_printing_changes(self):
        self.ensure_one()
        sections = self.env['shop.section'].search([('floor_id.pos_config_ids', '=', self.id)])
        domain = [('state', '=', 'draft'), ('section_id', 'in', sections.ids)]

        order_stats = self.env['pos.order']._read_group(domain, ['section_id'], ['__count'])
        linked_orderlines = self.env['pos.order.line'].search([('order_id.state', '=', 'draft'), ('order_id.section_id', 'in', sections.ids)])
        orders_map = {section.id: count for section, count in order_stats}
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
                skip_changes_map[line.order_id.section_id.id] += quantity_changed
            else:
                changes_map[line.order_id.section_id.id] += quantity_changed

        result = []
        for section in sections:
            result.append({'id': section.id, 'orders': orders_map.get(section.id, 0), 'changes': changes_map.get(section.id, 0), 'skip_changes': skip_changes_map.get(section.id, 0)})
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
            is_shop = 'module_pos_shop' not in vals or vals['module_pos_shop']
            if is_shop and 'iface_splitinvoice' not in vals:
                vals['iface_splitinvoice'] = True
            if not is_shop or not vals.get('iface_tipproduct', False):
                vals['set_tip_after_payment'] = False
        pos_configs = super().create(vals_list)
        for config in pos_configs:
            if config.module_pos_shop:
                self._setup_default_floor(config)
        return pos_configs

    def write(self, vals):
        if ('module_pos_shop' in vals and vals['module_pos_shop'] is False):
            vals['floor_ids'] = [(5, 0, 0)]

        if ('module_pos_shop' in vals and not vals['module_pos_shop']) or ('iface_tipproduct' in vals and not vals['iface_tipproduct']):
            vals['set_tip_after_payment'] = False

        if ('module_pos_shop' in vals and vals['module_pos_shop']):
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
                ('module_pos_shop', '=', True),
            ])
            if not pos_configs:
                pos_configs = self.env['pos.config'].with_company(company).create({
                'name': _('Bar'),
                'company_id': company.id,
                'module_pos_shop': True,
                'iface_splitinvoice': True,
                'iface_printinvoice': True,
                'iface_orderline_notes': True,

            })
            pos_configs.setup_defaults(company)

    def setup_defaults(self, company):
        main_shop = self.env.ref('pos_shop.pos_config_main_shop', raise_if_not_found=False)
        main_shop_is_present = main_shop and self.filtered(lambda cfg: cfg.id == main_shop.id)
        if main_shop_is_present:
            non_main_shop_configs = self - main_shop
            non_main_shop_configs.assign_payment_journals(company)
            main_shop._setup_main_shop_defaults()
            self.generate_pos_journal(company)
            self.setup_invoice_journal(company)
        else:
            super().setup_defaults(company)

    def _setup_main_shop_defaults(self):
        self.ensure_one()
        self._set_tips_after_payment_if_country_custom()
        self._link_same_non_cash_payment_methods_if_exists('point_of_sale.pos_config_main')
        self._ensure_cash_payment_method('MRCSH', _('Cash Shop'))

    def _setup_default_floor(self, pos_config):
        if not pos_config.floor_ids:
            main_floor = self.env['shop.floor'].create({
                'name': pos_config.company_id.name,
                'pos_config_ids': [(4, pos_config.id)],
            })
            self.env['shop.section'].create({
                'name': '1',
                'floor_id': main_floor.id,
                'seats': 1,
                'position_h': 100,
                'position_v': 100,
                'width': 100,
                'height': 100,
            })
