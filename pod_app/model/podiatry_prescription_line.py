# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_prescription_line(models.Model):
    _name = "podiatry.prescription.line"
    _description = 'podiatry prescription line'

    name = fields.Many2one('podiatry.prescription.order', 'Prescription ID')
    treatment_id = fields.Many2one('podiatry.treatment', 'Treatment')
    indication = fields.Char('Indication')
    allow_substitution = fields.Boolean('Allow Substitution')
    form = fields.Char('Form')
    prnt = fields.Boolean('Print')
    route = fields.Char('Administration Route')
    end_treatement = fields.Datetime('Administration Route')
    dose = fields.Float('Dose')
    dose_unit_id = fields.Many2one('podiatry.dose.unit', 'Dose Unit')
    qty = fields.Integer('x')
    device_dosage_id = fields.Many2one(
        'podiatry.device.dosage', 'Frequency')
    admin_times = fields.Char('Admin Hours', size=128)
    frequency = fields.Integer('Frequency')
    frequency_unit = fields.Selection([('seconds', 'Seconds'), ('minutes', 'Minutes'), (
        'hours', 'hours'), ('days', 'Days'), ('weeks', 'Weeks'), ('wr', 'When Required')], 'Unit')
    duration = fields.Integer('Treatment Duration')
    duration_period = fields.Selection([('minutes', 'Minutes'), ('hours', 'hours'), ('days', 'Days'), (
        'months', 'Months'), ('years', 'Years'), ('indefine', 'Indefine')], 'Treatment Period')
    quantity = fields.Integer('Quantity')
    review = fields.Datetime('Review')
    refills = fields.Integer('Refills#')
    short_comment = fields.Char('Comment', size=128)
    end_treatment = fields.Datetime('End of treatment')
    start_treatment = fields.Datetime('Start of treatment')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
