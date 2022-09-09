# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_inpatient_diet(models.Model):
    _name = 'podiatry.inpatient.diet'
    _description = 'Podiatry Inpatient Diet'

    diet_id = fields.Many2one(
        'podiatry.diet.therapeutic', string='Diet', required=True)
    remarks = fields.Text(string=' Remarks / Directions ')
    podiatry_inpatient_registration_id = fields.Many2one(
        'podiatry.inpatient.registration', string='Inpatient Id')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
