# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class om_hospital(models.Model):
#     _name = 'om_hospital.om_hospital'
#     _description = 'om_hospital.om_hospital'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
from datetime import date
from odoo import models, fields, api


class HospitalMedicine(models.Model):
    _name = 'syn.hospital.medicine'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Syn Medicine'
    _rec_name = 'med_name'


    med_name = fields.Char(string="Medicine Name")
    price = fields.Float(string="Medicine Price")
    qty = fields.Integer(string="Medicine Quantity")
    appointment_id = fields.Many2one('syn.hospital.appointment',string="Appointment")