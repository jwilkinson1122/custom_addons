# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class Doctor(models.Model):

    _name = "hospital.doctor"
    _description = "Doctor"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, tracking=True)
    surname = fields.Char(string="Surname", required=True, tracking=True)
    doctor_tc = fields.Char(string="TC NO", required=True)
    brans_kod = fields.Char(string="Branch Code", required=True)
    sertifika_kod = fields.Selection([
        ('0', 'Yok'),
        ('56', 'Hemodiyaliz'),
        ('109', 'Aile Hekimliği')
    ], string="Sertifika Kod", required=True)
    birth = fields.Date(string="Date of Birth",
                        date_format="dd.MM.yyyy", required=True)
    age = fields.Integer(string="Age", readonly=True, compute='_compute_age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], required=True, default='other', tracking=True)
    active = fields.Boolean(string='Active', default='True', tracking=True)
    image = fields.Image(string="Image")

    @api.depends('birth')
    def _compute_age(self):
        for rec in self:
            today = dateutil.utils.today()
            if rec.birth:
                rec.age = today.year - rec.birth.year
            else:
                rec.age = 0

    def name_get(self):
        result = []
        for rec in self:
            name = rec.doctor_tc + ' : ' + rec.name + ' ' + rec.surname
            result.append((rec.id, name))
        return result
