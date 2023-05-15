# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"
    _description = "Practice Partner"
    
    # force "active_test" domain to bypass _search() override
    child_ids = fields.One2many(
        domain=[("active", "=", True), ("is_company", "=", False)]
    )

    # force "active_test" domain to bypass _search() override
    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[("active", "=", True), ("is_company", "=", True)],
    )

    partner_type = fields.Selection([
        ('doctor', 'Doctor'), 
        ('receptionist', 'Receptionist'), 
        ('nurse', 'Nurse'), 
        ('administrator', 'Administrator'),
        ('other', 'Other')
         ], string='Partner Type', tracking=True)
 
    practice_type = fields.Selection([('clinic', 'Clinic'),
                                      ('hospital', 'Hospital'),
                                      ('military', 'Military (VA)'),
                                      ('other', 'Other')],
                                     default='clinic', string="Practice Type", tracking=True)
