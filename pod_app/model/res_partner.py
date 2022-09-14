# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class res_partner(models.Model):
    _inherit = 'res.partner'

    relationship = fields.Char(string='Relationship')
    relative_partner_id = fields.Many2one('res.partner', string="Relative_id")
    is_patient = fields.Boolean(string='Patient')
    is_person = fields.Boolean(string="Person")
    is_doctor = fields.Boolean(string="Doctor")
    is_insurance_company = fields.Boolean(string='Insurance Company')
    is_lab = fields.Boolean(string="Lab")
    patient_insurance_ids = fields.One2many('podiatry.insurance', 'patient_id')
    is_practice = fields.Boolean('Practice')
    company_insurance_ids = fields.One2many(
        'podiatry.insurance', 'insurance_compnay_id', 'Insurance')
    reference = fields.Char('ID Number')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
