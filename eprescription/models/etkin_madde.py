# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class EtkinMadde(models.Model):

    _name = "hospital.etkin_madde"
    _description = "Hospital Etkin Madde"
    _rec_name = 'etkin_madde_kodu'

    etkin_maddedvo_id = fields.Many2one(
        'hospital.etkin_maddedvo', string="Etkin Madde")
    etkin_madde_kodu = fields.Char(
        string="Active Item Code", related="etkin_maddedvo_id.etkin_madde_kodu")
    kullanim_doz1 = fields.Char(string="Kullanım Doz 1")
    kullanim_doz2 = fields.Char(string="Kullanım Doz 2")
    kullanim_doz_birimi = fields.Selection([
        ('1', 'Adet'),
        ('2', 'Mililitre'),
        ('3', 'Miligram'),
        ('4', 'Gram'),
        ('5', 'Damla'),
        ('6', 'Ünite'),
        ('7', 'Kutu'),
        ('8', 'Mikrogram'),
        ('9', 'Mikrolitre'),
        ('A', 'Bin Ünite'),
        ('B', 'Milyon Ünite')
    ], string="Kullanım Doz Birimi")
    kullanim_doz_periyot = fields.Char(string="Kullanım Doz Periyot")
    kullanim_doz_periyot_birimi = fields.Selection([
        ('3', 'Günde'),
        ('4', 'Haftada'),
        ('5', 'Ayda'),
        ('6', 'Yılda'),
    ])
