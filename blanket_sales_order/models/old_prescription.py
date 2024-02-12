# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
# from datetime import datetime, time
# from odoo.exceptions import Warning
from odoo.tools.misc import formatLang, get_lang

import logging
_logger = logging.getLogger(__name__)

class Prescription(models.Model):
    _name = 'prescription'
    _description = "Prescription"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = "id desc"

    @api.depends()
    def _get_sale_order(self):
        for rec in self:
            order_ids = self.env['sale.order'].search([('prescription_so_id', '=', self.id)])
            if order_ids:
                rec.order_count = len(order_ids.ids)
            else:
                rec.order_count = 0

    name = fields.Char(
        readonly=True,
        default=lambda self: _('New')
    )
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('ongoing', 'Ongoing'),
        ('done', 'Closed'),
        ('cancel', 'Cancelled'),
        ], 
        string='Status', 
        copy=False, 
        default='draft',
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True,
    )
    # prescriptioning_date = fields.Date(
    #     string="Ordering Date", 
    #     tracking=True,
    # )
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
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        required=True, 
        default=lambda self: self.env.company,
    )
    order_line = fields.One2many(
        'prescription.line', 
        'order_id', 
        string='Products to Sale'
    )
    pricelist_id = fields.Many2one(
        'product.pricelist', 
        string='Pricelist',
        required=True,
    )
    internal_note = fields.Text(
        'Internal Note'
    )  
    date_order = fields.Datetime(
        string='Order Date', 
        required=True, 
        index=True,
        tracking=True, 
        copy=False, 
        default=fields.Datetime.now, 
        help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders."
    )
    order_count = fields.Integer(
        string='Invoice Count', 
        compute='_get_sale_order', 
    )

    currency_id = fields.Many2one(
        related='pricelist_id.currency_id', 
        depends=["pricelist_id"], 
        store=True
    )

    def action_view_sale_order(self):
        orders = self.env['sale.order'].search([('prescription_so_id', '=', self.id)])
        # action = self.env.ref('sale.action_quotations_with_onboarding').sudo().read()[0]
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

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('prescription')
        return super(Prescription, self).create(vals)  

    def action_create_prescription_to_so(self):
        # action = self.env.ref('prescription.action_prescription_to_so').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('prescription.action_prescription_to_so')
        action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        line_list = []
        for rec in self:
            if rec.validity_start_date <= fields.Date.today() and rec.validity_end_date >= fields.Date.today():
                FiscalPosition = self.env['account.fiscal.position']
                fpos = FiscalPosition.get_fiscal_position(rec.partner_id.id)
                for line in rec.order_line:
                    # product_lang = line.product_id.with_context(
                    #     lang=rec.partner_id.lang,
                    #     partner_id=rec.partner_id.id
                    # )
                    # name = product_lang.display_name
                    # if product_lang.description_purchase:
                    #     name += '\n' + product_lang.description_purchase

                    # Compute taxes
                    if fpos:
                        taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == rec.company_id)).ids
                    else:
                        taxes_ids = line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == rec.company_id).ids


                    # Compute quantity and price_unit
                    if line.product_uom_id != line.product_id.uom_po_id:
                        product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                        price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
                    else:
                        product_qty = line.product_qty
                        price_unit = line.price_unit

                    order_line_values = line._prepare_sale_order_line(
                        name=line.name, product_qty=product_qty, price_unit=price_unit,
                        taxes_ids=taxes_ids)
                    line_list.append((0, 0, order_line_values))

                action['context'] = {
                    'default_partner_id': rec.partner_id.id,
                    'default_order_line': line_list,
                    'default_fiscal_position_id': fpos.id,
                    'default_payment_term_id': rec.partner_id.property_supplier_payment_term_id.id or False,
                    'default_company_id': rec.company_id.id,
                    'default_pricelist_id': rec.pricelist_id.id,
                    'default_note': rec.internal_note,
                    'default_origin': rec.name,
                    'default_prescription_so_id': rec.id
                }
        return action

class PrescriptionLine(models.Model):
    _name = "prescription.line"
    _description = "Prescription Line"
    _rec_name = 'product_id'

    order_id = fields.Many2one('prescription', 
        string='Sale Agreement', 
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        required=True
    )
    product_uom_id = fields.Many2one(
        'uom.uom', 
        string='Product Unit of Measure'
    )
    product_qty = fields.Float(
        string='Quantity', 
        digits='Product Unit of Measure'
    )
    price_unit = fields.Float(
        string='Unit Price', 
        digits='Product Price'
    )
    tax_id = fields.Many2many(
        'account.tax', 
        string='Taxes', 
    )
    company_id = fields.Many2one(
        related='order_id.company_id', 
        string='Company', 
        store=True, 
        readonly=True, 
        index=True
    )
    name = fields.Text(
        string='Description'
    )
    currency_id = fields.Many2one(
        related='order_id.currency_id', 
        depends=['order_id.currency_id'], 
        store=True, 
        string='Currency', 
        readonly=True
    )

    def get_sale_order_line_multiline_description_sale(self, product):
        """ Compute a default multiline description for this sales order line.

        In most cases the product description is enough but sometimes we need to append information that only
        exists on the sale order line itself.
        e.g:
        - custom attributes and attributes that don't create variants, both introduced by the "product configurator"
        - in event_sale we need to know specifically the sales order line as well as the product to generate the name:
          the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        return product.get_product_multiline_description_sale()

    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id) #odoo14
            fpos = line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            # line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes #odoo13
            #line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id) #odoo14
            line.tax_id = fpos.map_tax(taxes)

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.

        # if self.order_id.pricelist_id.discount_policy == 'with_discount':
        #     return product.with_context(pricelist=self.order_id.pricelist_id.id).price
        # product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom_id.id)

        # final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_qty or 1.0, self.order_id.partner_id)
        # base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_qty, self.product_uom_id, self.order_id.pricelist_id.id)
        # if currency != self.order_id.pricelist_id.currency_id:
        #     base_price = currency._convert(
        #         base_price, self.order_id.pricelist_id.currency_id,
        #         self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
        # # negative discounts (= surcharge) are included in the display price
        # return max(base_price, final_price)

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.order_id.pricelist_id.id, uom=self.product_uom_id.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom_id.id)

        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.product_qty or 1.0, self.order_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_qty, self.product_uom_id, self.order_id.pricelist_id.id)
        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_order_line.product_template_value_ids
        vals = {}
        if not self.product_uom_id or (self.product_id.uom_id.id != self.product_uom_id.id):
            vals['product_uom_id'] = self.product_id.uom_id
            vals['product_qty'] = self.product_qty or 1.0

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_qty') or self.product_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom_id.id
        )

        vals.update(name=self.get_sale_order_line_multiline_description_sale(product))

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = product._get_tax_included_unit_price(
                self.company_id,
                self.order_id.currency_id,
                self.order_id.date_order,
                'sale',
                product_price_unit=self._get_display_price(product),
                product_currency=self.order_id.currency_id
            )
            # vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}

        product = self.product_id
        if product and product.sale_line_warn != 'no-message':
            if product.sale_line_warn == 'block':
                self.product_id = False
            return {
                'warning': {
                    'title': _("Warning for %s", product.name),
                    'message': product.sale_line_warn_msg,
                }
            }

        # if product.sale_line_warn != 'no-message':
        #     title = _("Warning for %s") % product.name
        #     message = product.sale_line_warn_msg
        #     warning['title'] = title
        #     warning['message'] = message
        #     result = {'warning': warning}
        #     if product.sale_line_warn == 'block':
        #         self.product_id = False

        # return result

    @api.onchange('product_uom_id', 'product_qty')
    def product_uom_change(self):
        if not self.product_uom_id or not self.product_id:
            self.price_unit = 0.0
            return
        for line in self:
            if line.order_id.pricelist_id and line.order_id.partner_id:
                product = line.product_id.with_context(
                    lang=line.order_id.partner_id.lang,
                    partner=line.order_id.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order,
                    pricelist=line.order_id.pricelist_id.id,
                    uom=line.product_uom_id.id,
                    fiscal_position=line.order_id.partner_id.property_account_position_id
                )
                self.price_unit = product._get_tax_included_unit_price(
                    self.company_id or self.order_id.company_id,
                    self.order_id.currency_id,
                    self.order_id.date_order,
                    'sale',
                    fiscal_position=line.order_id.partner_id.property_account_position_id,
                    product_price_unit=self._get_display_price(product),
                    product_currency=self.order_id.currency_id
                )
                # line.price_unit = self.env['account.tax']._fix_tax_included_price_company(line._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

    def _prepare_sale_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        self.ensure_one()
        return {
            'name': name,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'product_uom_qty': product_qty,
            'price_unit': price_unit,
            'tax_id': [(6, 0, taxes_ids)],
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: