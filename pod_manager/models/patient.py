# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class Patient(models.Model):

    _name = "podiatry.patient"
    _description = "Podiatry Patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'tc_no'

    name = fields.Char(string='Name', required=True, tracking=True)
    surname = fields.Char(string='Surname', required=True, tracking=True)
    tc_no = fields.Char(string='TC NO', required=True, tracking=True)
    birth = fields.Date(string='Birth Date', date_format="dd.MM.yyyy")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], required=True, default='other', tracking=True)
    active = fields.Boolean(string='Active', default='True', tracking=True)
    image = fields.Image(string="Image")

    # partner_id = fields.Many2one(
    #     comodel_name='res.partner', string="Contact",
    # )

    # other_partner_ids = fields.Many2many(
    #     comodel_name='res.partner',
    #     relation='podiatry_patient_partners_rel',
    #     column1='patient_id', column2='partner_id',
    #     string="Other Contacts",
    # )

    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Doctor')

    is_patient = fields.Boolean()

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string="Practice",
    )

    doctor_id = fields.Many2one(
        comodel_name='podiatry.doctor',
        string="Doctor",
    )

    prescription_ids = fields.One2many('podiatry.prescription', 'patient_id')

    def name_get(self):
        result = []
        for rec in self:
            name = rec.tc_no + ' : ' + rec.name + ' ' + rec.surname
            result.append((rec.id, name))
        return result
