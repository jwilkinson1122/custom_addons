# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class  podiatry_patient_pregnency(models.Model):
    _name = 'podiatry.patient.pregnency'
    _description = 'podiatry patient pregnency'

    gravida = fields.Integer('Pregnancy #')
    lmp = fields.Integer('LMP')
    pdd = fields.Date('Pregnency  Due Date')
    patient_id= fields.Many2one('podiatry.patient','Patient')
    current_pregnency = fields.Boolean('Current Pregnency')
    podiatry_patient_evolution_prental_ids = fields.One2many('podiatry.patient.prental.evoultion', 'pregnency_id', 'Patient Perinatal Evaluations')
    podiatry_perinatal_ids = fields.One2many('podiatry.preinatal', 'pregnency_id', 'Podiatry Perinatal ')
    puerperium_perental_ids = fields.One2many('podiatry.puerperium.monitor', 'pregnency_id', 'Puerperium Monitor')
    fetuses = fields.Boolean('Fetuses')
    monozygotic = fields.Boolean('Monozygotic')
    igur = fields.Selection([('s','Symmetric'),('a','Asymmetric')], 'IGUR')
    warn = fields.Boolean('Warning')
    result = fields.Char('Result')
    pregnancy_end_date = fields.Date('Pregnancy End Date')
    pregnancy_end_result = fields.Char('Pregnancy End Result')


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
