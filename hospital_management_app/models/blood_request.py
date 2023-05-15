# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BloodRequest(models.Model):
    # _name = 'hospital.patient.registration'
    _name = 'blood.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Blood Request'

    # Identification Details

    partner_id = fields.Many2one('res.partner', string='Patient')
    name = fields.Char(string="Name")
    registration_no = fields.Char(string='Registration Card')
    employee_id = fields.Many2one('hr.employee', string='Referring Doctor')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    state = fields.Selection(
        [('draft', 'Draft'), ('issue', 'Issue'), ('cancel', 'cancel'), ('invoice', 'Invoice')], default='draft',
        tracking=True)
    date = fields.Datetime('Date')
    product_id = fields.Many2one('product.product', string='Blood Type(Group)')
    price_unit = fields.Float(string='Unit Price')
    quantity = fields.Float(string='Quantity', default=1)
    fees = fields.Float(string='Total Fees', compute='compute_fees')
    cancel_reason = fields.Text(string='Cancel Reason')
    picking_id = fields.Many2one('stock.picking', string='Outgoing Shipment')

    def action_issue(self):
        for rec in self:
            picking_line = {'name': rec.name,
                            'product_id': rec.product_id.id,
                            'product_uom_qty': self.quantity,
                            'reserved_availability': self.quantity,
                            'quantity_done': self.quantity,
                            'product_uom': rec.product_id.uom_id.id}
            picking_type_id = self.env.ref('stock.picking_type_out')
            location_id = self.env.ref('stock.stock_location_stock')
            location_dest_id = self.env.ref('stock.stock_location_customers')
            # picking depend on delivery picking type
            picking_data = {'move_ids_without_package': [(0, 0, picking_line)],
                            'picking_type_id': picking_type_id.id,
                            'state': 'draft',
                            'origin': self.name,
                            'location_id': location_id.id,
                            'location_dest_id': location_dest_id.id,
                            }
            picking_id = self.env['stock.picking'].create(picking_data)
            if picking_id:
                picking_id.action_confirm()
                picking_id.button_validate()
                rec.state = 'issue'
                rec.picking_id = picking_id

    def action_cancel(self):
        form_id = self.env.ref('hospital_management_app.view_blood_request_cancel').id
        return {'type': 'ir.actions.act_window',
                'name': _('Blood Cancel Reason'),
                'res_model': 'blood.request.cancel',
                'view_mode': ' form',
                'views': [(form_id, 'form')],
                'context': {
                    'default_request_id': self.id,
                },
                'target': 'new'
                }

    @api.depends('price_unit', 'quantity')
    def compute_fees(self):
        for rec in self:
            rec.fees = rec.quantity * rec.price_unit

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
        company_id = self.employee_id.company_id
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        journal = self.env['account.move'].with_context(default_type='out_invoice')._get_default_journal()
        if not journal:
            raise ValidationError(_('Please define an accounting sales journal for the company %s (%s).') % (
                company_id.name, company_id.id))
        name = self.partner_id.name + '-' + self.name
        account_id = self.partner_id.property_account_receivable_id

        partner_id = self.partner_id
        invoice_lines = []
        vals = {
            'product_id': self.product_id.id,
            'name': name,
            'price_unit': self.price_unit,
            'quantity': self.quantity,
        }
        invoice_lines.append((0, 0, vals))

        invoice_vals = {
            'move_type': 'out_invoice',
            'invoice_user_id': self.env.user and self.env.user.id,
            'partner_id': partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': invoice_lines,
            #'journal_id': journal.id,  # company comes from the journal
            'company_id': self.employee_id.company_id.id,
        }
        return invoice_vals

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('blood.request') or 'New'
        return super(BloodRequest, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            rec.registration_no = rec.partner_id.registration_no

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.price_unit = rec.product_id.list_price
