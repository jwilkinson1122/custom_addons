# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_insurance(models.Model):
    _name = 'podiatry.insurance'
    _description = 'podiatry insurance'
    _rec_name = 'insurance_compnay_id'

    number = fields.Char('Number')
    podiatry_insurance_partner_id = fields.Many2one(
        'res.partner', 'Owner', required=True)
    patient_id = fields.Many2one('res.partner', 'Owner')
    type = fields.Selection([('state', 'State'), ('private', 'Private'),
                            ('labour_union', 'Labour Union/ Syndical')], 'Insurance Type')
    member_since = fields.Date('Member Since')
    insurance_compnay_id = fields.Many2one('res.partner', domain=[(
        'is_insurance_company', '=', True)], string='Insurance Compnay')
    category = fields.Char('Category')
    notes = fields.Text('Extra Info')
    member_exp = fields.Date('Expiration Date')
    podiatry_insurance_plan_id = fields.Many2one(
        'podiatry.insurance.plan', 'Plan')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
