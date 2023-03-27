# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Jesni Banu and Nilmar Shereef(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PodiatryManagement(models.Model):
    _name = 'podiatry.order'
    _inherit = 'mail.thread'
    _description = "Podiatry Order"
    _order = 'order_date desc, id desc'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('podiatry.order')
        return super(PodiatryManagement, self).create(vals)

    @api.depends('order_lines')
    def get_total(self):
        total = 0
        for obj in self:
            for each in obj.order_lines:
                total += each.amount
            obj.total_amount = total

    def confirm_order(self):
        self.state = 'order'
        sale_obj = self.env['sale.order'].create(
            {'partner_id': self.partner_id.id,
             'partner_invoice_id': self.partner_invoice_id.id,
             'partner_shipping_id': self.partner_shipping_id.id})
        self.sale_obj = sale_obj
        product_id = self.env.ref('podiatry_management.podiatry_service')
        self.env['sale.order.line'].create({'product_id': product_id.id,
                                            'name': 'Podiatry Service',
                                            'price_unit': self.total_amount,
                                            'order_id': sale_obj.id
                                            })
        for each in self:
            for obj in each.order_lines:
                self.env['manufacturing.manufacturing'].create(
                    {'name': obj.product_id.name + '-Manufacturing',
                     'user_id': obj.manufacturing_type.assigned_person.id,
                     'description': obj.description,
                     'podiatry_obj': obj.id,
                     'state': 'draft',
                     'manufacturing_date': datetime.now().strftime(
                         '%Y-%m-%d %H:%M:%S')})

    def create_invoice(self):
        if self.sale_obj.state in ['draft', 'sent']:
            self.sale_obj.action_confirm()
        self.invoice_status = self.sale_obj.invoice_status
        return {
            'name': 'Create Invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.advance.payment.inv',
            'type': 'ir.actions.act_window',
            'context': {'podiatry_sale_obj': self.sale_obj.id},
            'target': 'new'
        }

    def return_dress(self):
        self.state = 'return'

    def cancel_order(self):
        self.state = 'cancel'

    def _invoice_count(self):
        wrk_ordr_ids = self.env['account.move'].search([('invoice_origin', '=', self.sale_obj.name)])
        self.invoice_count = len(wrk_ordr_ids)

    def _work_count(self):
        if self.id:
            wrk_ordr_ids = self.env['manufacturing.manufacturing'].search([('podiatry_obj.podiatry_obj.id', '=', self.id)])
            self.work_count = len(wrk_ordr_ids)
        else:
            self.work_count = False

    def action_view_podiatry_works(self):

        work_obj = self.env['manufacturing.manufacturing'].search(
            [('podiatry_obj.podiatry_obj.id', '=', self.id)])
        work_ids = []
        for each in work_obj:
            work_ids.append(each.id)
        view_id = self.env.ref('podiatry_management.manufacturing_form_view').id
        if work_ids:
            if len(work_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'manufacturing.manufacturing',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Works'),
                    'res_id': work_ids and work_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', work_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'manufacturing.manufacturing',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Works'),
                    # 'res_id': work_ids
                }
            return value

    def action_view_invoice(self):
        self.ensure_one()
        inv_obj = self.env['account.move'].search(
            [('invoice_origin', '=', self.sale_obj.name)])
        inv_ids = []
        for each in inv_obj:
            inv_ids.append(each.id)
        view_id = self.env.ref('account.view_move_form').id
        if inv_ids:
            if len(inv_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'res_id': inv_ids and inv_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', inv_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    # 'res_id': inv_ids
                }
            return value

    name = fields.Char(string="Label", copy=False)
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', invisible=1, related='sale_obj.invoice_status',
        store=True)
    sale_obj = fields.Many2one('sale.order', invisible=1)
    invoice_count = fields.Integer(compute='_invoice_count',
                                   string='# Invoice')
    work_count = fields.Integer(compute='_work_count', string='# Works')
    partner_id = fields.Many2one('res.partner', string='Customer',
                                 readonly=True,
                                 states={'draft': [('readonly', False)],
                                         'order': [('readonly', False)]},
                                 required=True,
                                 change_default=True, index=True,
                                 )
    partner_invoice_id = fields.Many2one('res.partner',
                                         string='Invoice Address',
                                         readonly=True, required=True,
                                         states={
                                             'draft': [('readonly', False)],
                                             'order': [('readonly', False)]},
                                         help="Invoice address for current sales order.")
    partner_shipping_id = fields.Many2one('res.partner',
                                          string='Delivery Address',
                                          readonly=True, required=True,
                                          states={
                                              'draft': [('readonly', False)],
                                              'order': [('readonly', False)]},
                                          help="Delivery address for current sales order.")
    order_date = fields.Datetime(string='Date', readonly=True, index=True,
                                 states={'draft': [('readonly', False)],
                                         'order': [('readonly', False)]},
                                 copy=False, default=fields.Datetime.now, )
    podiatry_person = fields.Many2one('res.users', string='Podiatry Person',
                                     required=1)
    order_lines = fields.One2many('podiatry.order.line', 'podiatry_obj',
                                  required=1, ondelete='cascade')
    total_amount = fields.Float(compute='get_total', string='Total', store=1)
    currency_id = fields.Many2one("res.currency", string="Currency")
    note = fields.Text(string='Terms and conditions')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('order', 'Podiatry Order'),
        ('process', 'Processing'),
        ('done', 'Done'),
        ('return', 'Returned'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True,
        track_visibility='onchange', default='draft')


class PodiatryManagementLine(models.Model):
    _name = 'podiatry.order.line'
    _description = "Podiatry Order Line"

    @api.depends('manufacturing_type', 'extra_work', 'qty')
    def get_amount(self):
        for obj in self:
            total = obj.manufacturing_type.amount * obj.qty
            for each in obj.extra_work:
                total += each.amount * obj.qty
            obj.amount = total

    product_id = fields.Many2one('product.product', string='Dress', required=1)
    qty = fields.Integer(string='No of items', required=1)
    description = fields.Text(string='Description')
    manufacturing_type = fields.Many2one('manufacturing.type', string='Manufacturing Type',
                                   required=1)
    extra_work = fields.Many2many('manufacturing.work', string='Extra Work')
    amount = fields.Float(compute='get_amount', string='Amount')
    podiatry_obj = fields.Many2one('podiatry.order', invisible=1)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('manufacture', 'Manufacturing'),
        ('extra_work', 'Make Over'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')


class ManufacturingType(models.Model):
    _name = 'manufacturing.type'
    _description = "Manufacturing TYpe"

    name = fields.Char(string='Name', required=1)
    assigned_person = fields.Many2one('res.users', string='Assigned Person',
                                      required=1)
    amount = fields.Float(string='Service Charge', required=1)


class ExtraWork(models.Model):
    _name = 'manufacturing.work'
    _description = 'Manufacturing Work'

    name = fields.Char(string='Name', required=1)
    assigned_person = fields.Many2one('res.users', string='Assigned Person',
                                      required=1)
    amount = fields.Float(string='Service Charge', required=1)


class Manufacturing(models.Model):
    _name = 'manufacturing.manufacturing'
    _description = 'Manufacturing Manufacturing'

    def start_manufacture(self):
        if not self.podiatry_works:
            self.podiatry_obj.state = 'manufacture'
            self.podiatry_obj.podiatry_obj.state = 'process'
        for each in self:
            for obj in each.product_line:
                self.env['sale.order.line'].create(
                    {'product_id': obj.product_id.id,
                     'name': obj.name,
                     'price_unit': obj.price_unit,
                     'order_id': each.podiatry_obj.podiatry_obj.sale_obj.id,
                     'product_uom_qty': obj.quantity,
                     'product_uom': obj.uom_id.id,
                     })
        self.state = 'process'

    def set_to_done(self):
        self.state = 'done'

        f = 0
        if not self.podiatry_works:
            if self.podiatry_obj.extra_work:
                for each in self.podiatry_obj.extra_work:
                    self.create({'name': each.name,
                                 'user_id': each.assigned_person.id,
                                 'description': self.podiatry_obj.description,
                                 'podiatry_obj': self.podiatry_obj.id,
                                 'state': 'draft',
                                 'podiatry_works': True,
                                 'manufacturing_date': datetime.now().strftime(
                                     '%Y-%m-%d %H:%M:%S')})
                self.podiatry_obj.state = 'extra_work'
        podiatry_obj = self.search([('podiatry_obj.podiatry_obj', '=',
                                    self.podiatry_obj.podiatry_obj.id)])
        for each in podiatry_obj:
            if each.state != 'done' or each.state == 'cancel':
                f = 1
                break
        if f == 0:
            self.podiatry_obj.podiatry_obj.state = 'done'
        podiatry_obj1 = self.search([('podiatry_obj', '=', self.podiatry_obj.id)])
        f1 = 0
        for each in podiatry_obj1:
            if each.state != 'done' or each.state == 'cancel':
                f1 = 1
                break
        if f1 == 0:
            self.podiatry_obj.state = 'done'

    @api.depends('product_line')
    def get_total(self):
        total = 0
        for obj in self:
            for each in obj.product_line:
                total += each.subtotal
            obj.total_amount = total

    name = fields.Char(string='Work')
    podiatry_works = fields.Boolean(default=False, invisible=1)
    user_id = fields.Many2one('res.users', string='Assigned Person')
    manufacturing_date = fields.Datetime(string='Date')
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')
    podiatry_obj = fields.Many2one('podiatry.order.line', invisible=1)
    product_line = fields.One2many('manufacture.order.line', 'manufacture_obj',
                                   string='Products', ondelete='cascade')
    total_amount = fields.Float(compute='get_total', string='Grand Total')


class SaleOrderInherit(models.Model):
    _name = 'manufacture.order.line'
    _description = 'Manufacturing Order LINE'

    @api.depends('price_unit', 'quantity')
    def compute_amount(self):
        total = 0
        for obj in self:
            total += obj.price_unit * obj.quantity
        obj.subtotal = total

    manufacture_obj = fields.Many2one('manufacturing.manufacturing', string='Order Reference',
                               ondelete='cascade')
    name = fields.Text(string='Description', required=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure ', required=True)
    quantity = fields.Integer(string='Quantity')
    product_id = fields.Many2one('product.product', string='Product')
    price_unit = fields.Float('Unit Price', default=0.0,
                              related='product_id.list_price')
    subtotal = fields.Float(compute='compute_amount', string='Subtotal',
                            readonly=True, store=True)


class PodiatryManagementInvoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        context = self._context
        if context.get('podiatry_sale_obj'):
            sale_orders = self.env['sale.order'].browse(
                context.get('podiatry_sale_obj'))

        else:
            sale_orders = self.env['sale.order'].browse(
                self._context.get('active_ids', []))
        if self.advance_payment_method == 'delivered':
            sale_orders._create_invoices()
        elif self.advance_payment_method == 'all':
            sale_orders._create_invoices()(final=True)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)

            self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)
            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_(
                        'The product used to invoice a down payment should have an invoice policy set to "Ordered'
                        ' quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_(
                        "The product used to invoice a down payment should be of type 'Service'. Please use another "
                        "product or update this product."))
                taxes = self.product_id.taxes_id.filtered(
                    lambda
                        r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids
                so_line = sale_line_obj.create({
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'tax_id': [(6, 0, tax_ids)],
                })
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _create_invoice(self, order, so_line, amount):
        if (
                self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (
                self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(
                _('The value of the down payment amount must be positive.'))
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.fixed_amount
            name = _('Down Payment')

        invoice_vals = {
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'ref': order.client_order_ref,
            'invoice_payment_term_id': order.payment_term_id.id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,

                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }
        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
        invoice = self.env['account.move'].create(invoice_vals)
        invoice.message_post_with_view('mail.message_origin_link',
                                       values={'self': invoice,
                                               'origin': order},
                                       subtype_id=self.env.ref(
                                           'mail.mt_note').id)
