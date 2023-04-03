# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CanteenOrder(models.Model):
    _name = 'canteen.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'CanteenOrder'

    partner_id = fields.Many2one('res.partner', string='Customer')
    name = fields.Char(string="Order No")
    invoice_id = fields.Many2one('account.move', string='Invoice')
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done'), ('invoice', 'Invoice')], default='draft',
        tracking=True)
    date = fields.Datetime('Date')
    total_bill = fields.Float(string='Total Bill', compute='compute_total_bill')
    line_ids = fields.One2many('canteen.order.line', 'order_id', string='Lines')

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    @api.depends('line_ids')
    def compute_total_bill(self):
        subtotal = 0
        for rec in self:
            for line_id in rec.line_ids:
                subtotal += line_id.quantity * line_id.price_unit
            rec.total_bill = subtotal

    def action_create_invoice(self):
        invoice_vals = self._prepare_invoice()
        account_move = self.env['account.move'].create(invoice_vals)

        if account_move:
            self.invoice_id = account_move
            self.state = 'invoice'
            account_move.action_post()
        form_id = self.env.ref('account.view_move_form').id
        return {'type': 'ir.actions.act_window',
                'name': _('Invoice'),
                'res_model': 'account.move',
                'view_mode': 'form',
                'views': [(form_id, 'form')],
                'domain': [('id', '=', self.invoice_id.id)],
                'res_id': account_move.id
                }

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        company_id = self.create_uid.company_id
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        # journal = self.env['account.move'].with_context(default_type='out_invoice')._get_default_journal()
        # if not journal:
        #     raise ValidationError(_('Please define an accounting sales journal for the company %s (%s).') % (
        #         company_id.name, company_id.id))
        name = self.partner_id.name + '-' + self.name
        account_id = self.partner_id.property_account_receivable_id

        partner_id = self.partner_id
        invoice_lines = []
        for line_id in self.line_ids:
            vals = {
                'product_id': line_id.product_id.id,
                'name': line_id.product_id.name,
                'price_unit': line_id.price_unit,
                'quantity': line_id.quantity,
            }
            invoice_lines.append((0, 0, vals))

        invoice_vals = {
            'move_type': 'out_invoice',
            'invoice_user_id': self.env.user and self.env.user.id,
            'partner_id': partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': invoice_lines,
            # #'journal_id': journal.id,  # company comes from the journal
            'company_id': self.create_uid.company_id.id,
        }
        return invoice_vals

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('canteen.order') or 'New'
        return super(CanteenOrder, self).create(vals)


class CanteenOrderLine(models.Model):
    # _name = 'hospital.patient.registration'
    _name = 'canteen.order.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'order_id'
    _description = 'Canteen Order Line'

    order_id = fields.Many2one('canteen.order', string='Canteen Order')
    product_id = fields.Many2one('product.product', string='Foods')
    price_unit = fields.Float(string='Unit Price')
    quantity = fields.Float(string='Quantity', default=1)
    subtotal = fields.Float(string="Sub Total", compute='compute_subtotal')

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.price_unit = rec.product_id.list_price

    @api.onchange('price_unit', 'quantity')
    def compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.price_unit * rec.quantity