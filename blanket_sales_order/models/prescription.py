# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'ongoing', 'done', 'cancel'}
}

class Prescription(models.Model):
    _name = 'prescription'
    _description = "Prescription"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = "id desc"

    name = fields.Char(
        string="Order Reference",
        required=True, copy=False, readonly=True,
        index='trigram',
        # states={'draft': [('readonly', False)]},
        default=lambda self: _('New')
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True, readonly=False, change_default=True, index=True,
        tracking=1,
        # states=READONLY_FIELD_STATES,
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id))]"
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Quotation'),
            ('ongoing', 'Ongoing'),
            ('done', 'Closed'),
            ('cancel', 'Cancelled'),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft'
    )
    validity_start_date = fields.Date(
        string='Validity Start Date',
        tracking=True,
        required=True,
    )
    validity_end_date = fields.Date(
        string='Validity End Date',
        tracking=True,
        required=True,
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Sale Representative',
        default=lambda self: self.env.user,
    )
    order_line = fields.One2many(
        'prescription.line', 
        'order_id', 
        # states=READONLY_FIELD_STATES,
        string='Products to Sale'
    )
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True, required=True,  # Unrequired company
        # states=READONLY_FIELD_STATES,
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected."
    )
    note = fields.Html(
        string="Terms and conditions",
        # states=READONLY_FIELD_STATES,
    )
    date_order = fields.Datetime(
        string="Order Date",
        required=True, readonly=False, copy=False,
        # states=READONLY_FIELD_STATES,
        help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.",
        default=fields.Datetime.now
    )
    order_count = fields.Integer(
        string='Invoice Count', 
        compute='_get_sale_order', 
    )
    currency_id = fields.Many2one(
        related='pricelist_id.currency_id',
        depends=["pricelist_id"],
        store=True, 
        # precompute=True, 
        ondelete="restrict"
    )

    @api.depends('partner_id')
    def _compute_pricelist_id(self):
        for order in self:
            if not order.partner_id:
                order.pricelist_id = False
                continue
            order = order.with_company(order.company_id)
            order.pricelist_id = order.partner_id.property_product_pricelist

    @api.depends()
    def _get_sale_order(self):
        for rec in self:
            order_ids = self.env['sale.order'].search([('prescription_so_id', '=', self.id)])
            if order_ids:
                rec.order_count = len(order_ids.ids)
            else:
                rec.order_count = 0

    def action_view_sale_order(self):
        orders = self.env['sale.order'].search([('prescription_so_id', '=', self.id)])
        action = self.env['ir.actions.act_window']._for_xml_id('sale.action_quotations_with_onboarding')
        action['domain'] = [('id', 'in', orders.ids)]
        return action

    def action_confirm(self):
        self.write({
            'state': 'ongoing'
        })

    def action_close(self):
        self.write({
            'state': 'done'
        })

    def action_cancel(self):
        self.write({
            'state': 'cancel'
        })

    def action_draft(self):
        self.write({
            'state': 'draft'
        })

    # @api.model
    # def create(self, vals):
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('prescription')
        # return super(Prescription, self).create(vals)
        return super(Prescription, self).create(vals_list)

    def action_create_prescription_to_so(self):
        action = self.env['ir.actions.act_window']._for_xml_id('prescription.action_prescription_to_so')
        action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        line_list = []
        for rec in self:
            if rec.validity_start_date <= fields.Date.today() and rec.validity_end_date >= fields.Date.today():
                FiscalPosition = self.env['account.fiscal.position']
                fpos = FiscalPosition._get_fiscal_position(rec.partner_id)
                for line in rec.order_line:
                    # Compute taxes
                    if fpos:
                        taxes_ids = fpos.map_tax(line.product_id.taxes_id.filtered(lambda tax: tax.company_id == rec.company_id)).ids
                    else:
                        taxes_ids = line.product_id.taxes_id.filtered(lambda tax: tax.company_id == rec.company_id).ids

                    # Compute quantity and price_unit
                    if line.product_uom != line.product_id.uom_po_id:
                        product_qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_po_id)
                        price_unit = line.product_uom._compute_price(line.price_unit, line.product_id.uom_po_id)
                    else:
                        product_qty = line.product_uom_qty
                        price_unit = line.price_unit

                    order_line_values = line._prepare_sale_order_line(
                        name=line.name, product_qty=product_qty, price_unit=price_unit,
                        taxes_ids=taxes_ids)
                    
                    line_list.append((0, 0, order_line_values))

                vals = {
                    'partner_id': rec.partner_id.id,
                    'order_line': line_list,
                    'fiscal_position_id': fpos.id,
                    'payment_term_id': rec.partner_id.property_supplier_payment_term_id.id or False,
                    'company_id': rec.company_id.id,
                    'pricelist_id': rec.pricelist_id.id,
                    'note': rec.note,
                    'origin': rec.name,
                    'prescription_so_id': rec.id
                }
                new_sale_order = self.env['sale.order'].create(vals)
                action['res_id'] = new_sale_order.id
        return action

class PrescriptionLine(models.Model):
    _name = "prescription.line"
    _description = "Prescription Line"
    _rec_name = 'product_id'

    order_id = fields.Many2one(
        'prescription', 
        string='Sale Agreement', 
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', check_company=True, index='btree_not_null',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_product_uom',
        store=True, readonly=False, precompute=True, ondelete='restrict',
        domain="[('category_id', '=', product_uom_category_id)]"
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure', default=1.0,
        required=True, 
        # precompute=True
    )
    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True
    )
    company_id = fields.Many2one(
        related='order_id.company_id',
        store=True, index=True, 
        # precompute=True
    )
    name = fields.Text(
        string="Description",
        compute='_compute_name',
        store=True, readonly=False, required=True, precompute=True
    )
    currency_id = fields.Many2one(
        related='order_id.currency_id',
        depends=['order_id.currency_id'],
        store=True, 
        # precompute=True
    )
    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id', 
        depends=['product_id']
    )
    pricelist_item_id = fields.Many2one(
        comodel_name='product.pricelist.item',
        compute='_compute_pricelist_item_id'
    )

    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            if not line.product_id:
                continue

            name = line.with_context(lang=line.order_id.partner_id.lang)._get_sale_order_line_multiline_description_sale()
            line.name = name

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
                line.product_uom = line.product_id.uom_id

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if not line.product_uom or not line.product_id or not line.order_id.pricelist_id:
                line.price_unit = 0.0
            else:
                price = line.with_company(line.company_id)._get_display_price()
                FiscalPosition = self.env['account.fiscal.position']
                fpos = FiscalPosition._get_fiscal_position(line.order_id.partner_id)
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.order_id.currency_id,
                    line.order_id.date_order,
                    'sale',
                    fiscal_position=fpos,
                    product_price_unit=price,
                    product_currency=line.currency_id
                )

    def _get_display_price(self):
        """Compute the displayed unit price for a given line.

        Overridden in custom flows:
        * where the price is not specified by the pricelist
        * where the discount is not specified by the pricelist

        Note: self.ensure_one()
        """
        self.ensure_one()

        pricelist_price = self._get_pricelist_price()

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return pricelist_price

        if not self.pricelist_item_id:
            # No pricelist rule found => no discount from pricelist
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)

    def _get_pricelist_price(self):
        """Compute the price given by the pricelist for the given line information.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_rule = self.pricelist_item_id
        order_date = self.order_id.date_order or fields.Date.today()
        product = self.product_id
        qty = self.product_uom_qty or 1.0
        uom = self.product_uom or self.product_id.uom_id

        price = pricelist_rule._compute_price(
            product, qty, uom, order_date, currency=self.currency_id)

        return price

    def _get_sale_order_line_multiline_description_sale(self):
        """ Compute a default multiline description for this sales order line.

        In most cases the product description is enough but sometimes we need to append information that only
        exists on the sale order line itself.
        e.g:
        - custom attributes and attributes that don't create variants, both introduced by the "product configurator"
        - in event_sale we need to know specifically the sales order line as well as the product to generate the name:
          the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        self.ensure_one()
        return self.product_id.get_product_multiline_description_sale() 

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_pricelist_item_id(self):
        for line in self:
            if not line.product_id or not line.order_id.pricelist_id:
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order,
                )

    def _get_pricelist_price_before_discount(self):
        """Compute the price used as base for the pricelist price computation.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_rule = self.pricelist_item_id
        order_date = self.order_id.date_order or fields.Date.today()
        product = self.product_id
        qty = self.product_uom_qty or 1.0
        uom = self.product_uom

        if pricelist_rule:
            pricelist_item = pricelist_rule
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                # Find the lowest pricelist rule whose pricelist is configured
                # to show the discount to the customer.
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    rule_id = pricelist_item.base_pricelist_id._get_product_rule(
                        product, qty, uom=uom, date=order_date)
                    pricelist_item = self.env['product.pricelist.item'].browse(rule_id)

            pricelist_rule = pricelist_item

        price = pricelist_rule._compute_base_price(
            product,
            qty,
            uom,
            order_date,
            target_currency=self.currency_id,
        )

        return price

    def _prepare_sale_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        self.ensure_one()
        return {
            'name': name,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'product_uom_qty': product_qty,
            'price_unit': price_unit,
            # 'tax_id': [(6, 0, taxes_ids)],
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: