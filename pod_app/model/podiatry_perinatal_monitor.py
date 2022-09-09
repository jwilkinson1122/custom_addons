# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_perinatal_monitor(models.Model):

    _name = 'podiatry.perinatal.monitor'
    _description = 'podiatry perinatal monitor'

    podiatry_perinatal_id = fields.Many2one('podiatry.perinatal.monitor')
    date = fields.Date('Date')
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    mothers_heart_freq = fields.Integer('Mothers Heart Freq')
    consentration = fields.Integer('Consentration')
    cervix_dilation = fields.Integer('Cervix Dilation')
    fundel_height = fields.Integer('Fundel Height')
    fetus_presentation = fields.Selection([('n', 'Correct'),
                                           ('o', 'Occiput /Cephalic Postrior'),
                                           ('fb', 'Frank Breech'),
                                           ('cb', 'Complete Breech'),
                                           ('tl', 'Transverse Lie'),
                                           ('fu', 'Footling Lie')], 'Fetus Presentation')
    f_freq = fields.Integer('Fetus Heart Frequency')
    bleeding = fields.Boolean('Bleeding')
    meconium = fields.Boolean('Meconium')
    notes = fields.Char('Notes')


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
