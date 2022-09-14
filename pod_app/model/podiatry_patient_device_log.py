# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import date, datetime


class podiatry_patient_device_log(models.Model):
    _name = 'podiatry.patient.device.log'
    _description = 'Podiatry Patient device Log'

    admin_time = fields.Datetime(string='Date', readonly=True)
    quantity = fields.Float(string='Quantity')
    remarks = fields.Text(string='Remarks')
    podiatry_patient_device_log_id = fields.Many2one(
        'podiatry.physician', string='Health Professional', readonly=True)
    podiatry_quantity_unit_id = fields.Many2one(
        'podiatry.quantity.unit', string='Quantity Unt')
    podiatry_patient_log_treatment_id = fields.Many2one(
        'podiatry.patient.device', string='Log History')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
