# -*- coding: utf8 -*-

from odoo import models, fields, api


class Medicine(models.Model):
    _name = "hospital.medicine"
    _description = "Hospital Medicines"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "barcode"

    barcode = fields.Char(string="Barcode", required=True)
    name = fields.Char(string="Name", required=True)
    list_price = fields.Float(string="Price")
    geri_odeme_kapsami = fields.Selection([
        ('evet', 'Evet'),
        ('hayir', 'Hayır')
    ], string="Geri Ödeme Kapsamında mı?")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.barcode + ' : ' + rec.name
            result.append((rec.id, name))
        return result
