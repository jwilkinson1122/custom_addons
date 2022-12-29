from odoo import models, fields, api, _
from datetime import time


class Service(models.Model):
    _name = 'pet_clinic.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    }

    service_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                             index=True, default=lambda self: _('New'))
    rec_name = fields.Char(string='Recname',
                           compute='_compute_fields_rec_name')
    date_start = fields.Datetime(
        string='Date Start', required=True)
    date_end = fields.Datetime(
        string='Date End')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_process', 'In Process'),
        ('done', 'done'),
        ('canceled', 'canceled'),
    ], string='Status', default='draft')
    description = fields.Text(string='Description')

    # Item
    item_service = fields.Many2one(
        'pet_clinic.item', string='Service', required=True, domain="[('item_type', '=', 'service')]")
    service_name = fields.Char(related='item_service.name')

    # Visitation
    visitation = fields.Many2one(
        'pet_clinic.visitation', string='visitation ID', required=True)
    visitation_pet_name = fields.Char(
        related='visitation.pet_name', string='Pet')
    visitation_doctor_name = fields.Char(
        related='visitation.doctor_name', string='Doctor')

    @api.model
    def create(self, vals):
        if vals.get('service_id', _('New')) == _('New'):
            vals['service_id'] = self.env['ir.sequence'].next_by_code(
                'pet_service.seq') or _('New')
        result = super(Service, self).create(vals)
        return result

    @api.depends('visitation_pet_name', 'service_name')
    def _compute_fields_rec_name(self):
        for rec in self:
            rec.rec_name = '{} - {}'.format(rec.visitation_pet_name,
                                            rec.service_name)

    def action_check(self):
        for rec in self:
            rec.state = 'in_process'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'canceled'
