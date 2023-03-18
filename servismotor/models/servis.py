from odoo import api, fields, models


class Servis(models.Model):
    _name = 'servismotor.servis'
    _description = 'Servis Kendaraan'

    nomor = fields.Integer(string='No')
    kode = fields.Char(string='Kode Servis')
    name = fields.Char(string='Layanan Servis')
    stok = fields.Integer(string='Maintenance')
    harga = fields.Integer(string='Biaya')

