# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import date, datetime


class podiatry_patient_device_admin_time(models.Model):
    _name = 'podiatry.patient.device.admin.time'
    _description = 'Podiatry Patient Device Admin Time'

    admin_time = fields.Datetime(string='Date')
    quantity = fields.Float(string='Quantity')
    remarks = fields.Text(string='Remarks')
    podiatry_patient_admin_time_id = fields.Many2one(
        'podiatry.physician', string='Health Professional')
    quantity_unit = fields.Many2one(
        'podiatry.quantity.unit', string='Quantity Unt')
    podiatry_patient_admin_time_treatment_id = fields.Many2one(
        'podiatry.patient.device', string='Admin Time')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
