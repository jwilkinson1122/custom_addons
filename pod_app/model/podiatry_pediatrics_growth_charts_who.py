# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_pediatrics_growth_charts_who(models.Model):
    _name = 'podiatry.pediatrics.growth.charts.who'
    _description = 'podiatry pediatrics growth charts who'

    name = fields.Selection([
        ('l/h-f-a', 'Length/height For age'),
        ('w-f-a', 'Weight for age'),
        ('bmi-f-a', 'Body mass index for age (BMI for age)')],
        string='Indicator')
    sex = fields.Selection([('m', 'Male'), ('f', 'Female')], string='sex')
    measure = fields.Selection(
        [('p', 'percentile'), ('z', 'Z-scores')], string='Measure')
    type = fields.Char(string="Type")
    month = fields.Integer(string="Month")
    value = fields.Float(string='Value')
