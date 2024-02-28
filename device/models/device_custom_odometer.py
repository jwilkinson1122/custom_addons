# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class DeviceCustomOdometer(models.Model):
    _name = 'device.custom.odometer'
    _description = 'Odometer log for a custom'
    _order = 'date desc'

    name = fields.Char(compute='_compute_custom_log_name', store=True)
    date = fields.Date(default=fields.Date.context_today)
    value = fields.Float('Odometer Value', group_operator="max")
    custom_id = fields.Many2one('device.custom', 'Custom', required=True)
    unit = fields.Selection(related='custom_id.odometer_unit', string="Unit", readonly=True)
    driver_id = fields.Many2one(related="custom_id.driver_id", string="Driver", readonly=False)

    @api.depends('custom_id', 'date')
    def _compute_custom_log_name(self):
        for record in self:
            name = record.custom_id.name
            if not name:
                name = str(record.date)
            elif record.date:
                name += ' / ' + str(record.date)
            record.name = name

    @api.onchange('custom_id')
    def _onchange_custom(self):
        if self.custom_id:
            self.unit = self.custom_id.odometer_unit
