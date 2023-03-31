# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PodiatryDeviceLogServices(models.Model):
    _name = 'podiatry.device.log.services'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'service_type_id'
    _description = 'Services for devices'

    active = fields.Boolean(default=True)
    device_id = fields.Many2one('podiatry.device', 'Device', required=True, help='Device concerned by this log')
    amount = fields.Monetary('Cost')
    description = fields.Char('Description')
    laterality_id = fields.Many2one('podiatry.device.laterality', 'Laterality', help='Laterality measure of the device at the moment of this log')
    laterality = fields.Float(
        compute="_get_laterality", inverse='_set_laterality', string='Laterality Value',
        help='Laterality measure of the device at the moment of this log')
    laterality_unit = fields.Selection(related='device_id.laterality_unit', string="Unit", readonly=True)
    date = fields.Date(help='Date when the cost has been executed', default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    purchaser_id = fields.Many2one('res.partner', string="Patient", compute='_compute_purchaser_id', readonly=False, store=True)
    inv_ref = fields.Char('Vendor Reference')
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    notes = fields.Text()
    service_type_id = fields.Many2one(
        'podiatry.service.type', 'Service Type', required=True,
        default=lambda self: self.env.ref('podiatry.type_service_service_8', raise_if_not_found=False),
    )
    state = fields.Selection([
        ('new', 'New'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='new', string='Stage', group_expand='_expand_states')

    def _get_laterality(self):
        self.laterality = 0
        for record in self:
            if record.laterality_id:
                record.laterality = record.laterality_id.value

    def _set_laterality(self):
        for record in self:
            if not record.laterality:
                raise UserError(_('Emptying the laterality value of a device is not allowed.'))
            laterality = self.env['podiatry.device.laterality'].create({
                'value': record.laterality,
                'date': record.date or fields.Date.context_today(record),
                'device_id': record.device_id.id
            })
            self.laterality_id = laterality

    @api.model_create_multi
    def create(self, vals_list):
        for data in vals_list:
            if 'laterality' in data and not data['laterality']:
                # if received value for laterality is 0, then remove it from the
                # data as it would result to the creation of a
                # laterality log with 0, which is to be avoided
                del data['laterality']
        return super(PodiatryDeviceLogServices, self).create(vals_list)

    @api.depends('device_id')
    def _compute_purchaser_id(self):
        for service in self:
            service.purchaser_id = service.device_id.patient_id

    def _expand_states(self, states, domain, order):
        return [key for key, dummy in type(self).state.selection]
