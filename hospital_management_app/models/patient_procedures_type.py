# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class PatientProceduresType(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Patient Procedures Type'
    _name = 'patient.procedures.type'

    name = fields.Char(string='Name', required=True, tracking=True)
    fees = fields.Float(string='Fees', tracking=True)
    note = fields.Text(string='Note')
