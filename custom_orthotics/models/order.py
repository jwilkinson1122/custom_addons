from odoo import fields, models, api, _
from datetime import time


class Order(models.Model):
    _name = 'custom_orthotics.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'order_id'
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_hold': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    }

    # _defaults = {
    #     'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    #     'date_end': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    # }

    order_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))
    date = fields.Datetime(string='Date', required=True)
    date_hold = fields.Datetime(
        string='Hold Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_process', 'In Process'),
        ('done', 'done'),
        ('canceled', 'canceled'),
        ('hold', 'On Hold'),
    ], string='Status', default='draft')
    description = fields.Text(string='Description')

    # Owner
    owner = fields.Many2one(
        'custom_orthotics.doctor', required=True)
    owner_id = fields.Integer(related='owner.id')

    # Patient
    patient = fields.Many2one('custom_orthotics.patient', required=True,
                              domain="[('owner', '=', owner)]")
    patient_rec_name = fields.Char(
        related='patient.rec_name', string='Patient Recname')
    patient_id = fields.Integer(related='patient.id', string='Patient')
    patient_name = fields.Char(related='patient.name', string='Patient')

    # Practice
    practice = fields.Many2one(
        'custom_orthotics.practice', required=True)
    practice_name = fields.Char(related='practice.name', string='Practice')

    @api.model
    def create(self, vals):
        if vals.get('order_id', _('New')) == _('New'):
            vals['order_id'] = self.env['ir.sequence'].next_by_code(
                'patient_order.seq') or _('New')
        result = super(Order, self).create(vals)
        return result

    def action_check(self):
        for rec in self:
            rec.state = 'in_process'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'canceled'

    def action_hold(self):
        for rec in self:
            rec.state = 'hold'
