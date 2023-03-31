# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PodiatryDeviceAssignationLog(models.Model):
    _name = "podiatry.device.assignation.log"
    _description = "Patients history on a device"
    _order = "create_date desc, date_start desc"

    device_id = fields.Many2one('podiatry.device', string="Device", required=True)
    patient_id = fields.Many2one('res.partner', string="Patient", required=True)
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
