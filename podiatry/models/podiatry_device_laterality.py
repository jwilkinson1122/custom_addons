# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PodiatryDeviceLaterality(models.Model):
    _name = 'podiatry.device.laterality'
    _description = 'Laterality log for a device'
    _order = 'date desc'

    name = fields.Char(compute='_compute_device_log_name', store=True)
    date = fields.Date(default=fields.Date.context_today)
    value = fields.Selection(
        [('lt', 'Left Only'), ('rt', 'Right Only'), ('bl', 'Bilateral'),], 'Laterality', default='bl', help='Foot side unit ')
    device_id = fields.Many2one('podiatry.device', 'Device', required=True)
    unit = fields.Selection(related='device_id.laterality_unit', string="Unit", readonly=True)
    patient_id = fields.Many2one(related="device_id.patient_id", string="Patient", readonly=False)

    @api.depends('device_id', 'date')
    def _compute_device_log_name(self):
        for record in self:
            name = record.device_id.name
            if not name:
                name = str(record.date)
            elif record.date:
                name += ' / ' + str(record.date)
            record.name = name

    @api.onchange('device_id')
    def _onchange_device(self):
        if self.device_id:
            self.unit = self.device_id.laterality_unit
