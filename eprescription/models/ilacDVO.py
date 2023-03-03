# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class IlacDVO(models.Model):

    _name = "hospital.ilac"
    _description = "Product Chart"
    _rec_name = "barcode"

    barcode = fields.Char(string="Item Barcode")
    ilac_adi = fields.Char(string="Item Name")
    sgk_ilac_kodu = fields.Char(string="Insurance Code")
    ambalaj_miktari = fields.Float(string="Packing Qty")
    tek_doz_miktari = fields.Float(string="Single Amount")
    kutu_birim_miktari = fields.Float(string="Box Qty")
    ayaktan_odenme_sarti = fields.Selection([
        ('1', 'Payable'),
        ('2', 'Paid by Report'),
        ('3', 'Not Payable')
    ], string="Walk In Payment")
    yatan_odenme_sarti = fields.Selection([
        ('1', 'Payable'),
        ('2', 'Paid by Report'),
        ('3', 'Not Payable')
    ], string="Outstanding Payment Terms")
    etkin_madde_kodu = fields.Char(string="Active Item Code")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.barcode + ' : ' + rec.ilac_adi
            result.append((rec.id, name))
        return result
