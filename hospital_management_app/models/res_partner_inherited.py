# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"
    _description = "Practice Partner"
    
    is_doctor = fields.Boolean(string='Is Doctor', tracking=True)
    is_receptionist = fields.Boolean(string='Is Receptionist', tracking=True)
    is_administrator = fields.Boolean(string='Is Administrator', tracking=True)
    is_nurse = fields.Boolean(string='Is Nurse', tracking=True)
    is_patient = fields.Boolean(string='Is Patient', tracking=True)
    
    is_clinic = fields.Boolean(string='Is Clinic', tracking=True)
    is_hospital = fields.Boolean(string='Is Hospital', tracking=True)
    is_military = fields.Boolean(string='Is Military', tracking=True)
    is_other = fields.Boolean(string='Is Other', tracking=True)

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
    
    partner_type_id = fields.Many2one(
        comodel_name="partner.type", string="Partner Type"
    )
    
    practice_type_id = fields.Many2one(
        comodel_name="practice.type", string="Practice Type"
    )
    


    # employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")



    # partner_type = fields.Selection([
    #     ('doctor', 'Doctor'), 
    #     ('receptionist', 'Receptionist'), 
    #     ('nurse', 'Nurse'), 
    #     ('administrator', 'Administrator'),
    #     ('other', 'Other')
    #      ], string='Partner Type', tracking=True)
 
    # practice_type = fields.Selection([('clinic', 'Clinic'),
    #                                   ('hospital', 'Hospital'),
    #                                   ('military', 'Military (VA)'),
    #                                   ('other', 'Other')],
    #                                  default='clinic', string="Practice Type", tracking=True)

class PartnerType(models.Model):

    _name = "partner.type"
    _description = "Partner Type"

    id = fields.Integer(readonly=True)
    name = fields.Char(string="Title", required=True, translate=True)
    code = fields.Char(required=True)  # Readonly if id
    sequence = fields.Integer('Priority', default=10)
    active = fields.Boolean(default=True)
    shortcut = fields.Char(string="Abbreviation", translate=True)
    
    doctor = fields.Boolean(string='Is a Doctor', help="Check this box if this contact is a doctor.")
    receptionist = fields.Boolean(string='Is a Receptionist', help="Check this box if this contact is a receptionist.")
    administrator = fields.Boolean(string='Is an Administrator', help="Check this box if this contact is an administrator.")
    nurse = fields.Boolean(string='Is a nurse', help="Check this box if this contact is a nurse.")
    patient = fields.Boolean(string='Is a Patient', help="Check this box if this contact is a patient.")
    other = fields.Boolean(string='Is Other', help="Check this box if this contact is other.")
    
    parent_relation_label = fields.Char('Parent relation label', translate=True, required=True, default='Attached To:')

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Partner Type already exists!")
    ]

class PracticeType(models.Model):

    _name = "practice.type"
    _description = "Practice Type"

    id = fields.Integer(readonly=True)
    name = fields.Char(string="Title", required=True, translate=True)
    code = fields.Char(required=True)  # Readonly if id
    sequence = fields.Integer('Priority', default=10)
    active = fields.Boolean(default=True)
    shortcut = fields.Char(string="Abbreviation", translate=True)
    
    clinic = fields.Boolean(string='Is a Clinic', help="Check this box if this type is a clinic.")
    hospital = fields.Boolean(string='Is a Hospital', help="Check this box if this type is a hospital.")
    military = fields.Boolean(string='Is Military', help="Check this box if this type is a military facility.")
    other = fields.Boolean(string='Is Other', help="Check this box if this type is other.")
    
    _sql_constraints = [
        ("name_uniq", "unique (name)", "Practice Type already exists!")
    ]
