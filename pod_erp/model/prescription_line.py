# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class prescription_line(models.Model):
    _name = "podiatry.prescription.line"
    _description = 'podiatry prescription line'

    name = fields.Many2one('podiatry.prescription.order','Prescription ID')
    orthotic_id = fields.Many2one('podiatry.orthotic','Orthotic')
    indication = fields.Char('Indication')
    allow_substitution = fields.Boolean('Allow Substitution')
    form = fields.Char('Form')
    prnt = fields.Boolean('Print')
    route = fields.Char('Administration Route')
    quant = fields.Float('Quantity')
    quant_unit_id = fields.Many2one('podiatry.quant.unit', 'Quantity Unit')
    qty = fields.Integer('x')
    orthotic_measure_id = fields.Many2one('podiatry.orthotic.measure','Frequency')
    admin_times = fields.Char('Admin Hours', size = 128)
    frequency = fields.Integer('Frequency')
    frequency_unit = fields.Selection([('seconds','Seconds'),('minutes','Minutes'),('hours','hours'),('days','Days'),('weeks','Weeks'),('wr','When Required')], 'Unit')
    duration = fields.Integer('Treatment Duration')
    duration_period = fields.Selection([('minutes','Minutes'),('hours','hours'),('days','Days'),('months','Months'),('years','Years'),('indefine','Indefine')],'Treatment Period')
    quantity = fields.Integer('Quantity')
    review = fields.Datetime('Review')
    refills = fields.Integer('Refills#')
    short_comment = fields.Char('Comment', size=128 )



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
