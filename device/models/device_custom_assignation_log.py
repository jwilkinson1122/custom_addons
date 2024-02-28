# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class DeviceCustomAssignationLog(models.Model):
    _name = "device.custom.assignation.log"
    _description = "Drivers history on a custom"
    _order = "create_date desc, date_start desc"

    custom_id = fields.Many2one('device.custom', string="Custom", required=True)
    driver_id = fields.Many2one('res.partner', string="Driver", required=True)
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")

    @api.depends('driver_id', 'custom_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'{rec.custom_id.name} - {rec.driver_id.name}'
