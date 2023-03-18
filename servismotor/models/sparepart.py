from odoo import api, fields, models


class sparepart(models.Model):
    _name = 'servismotor.sparepart'
    _description = 'Sparepart Motor'

    nomor = fields.Integer(string='No')
    kode = fields.Char(string='Kode Barang')
    name = fields.Char(string='Nama Barang')
    stok = fields.Integer(string='Stok Barang')

    harga_beli = fields.Integer(
        string='Harga_beli', 
        required=False)

    harga_jual = fields.Integer(
        string='Harga_jual', 
        required=False)
    satuan = fields.Selection(
        string='Satuan',
        selection=[('pcs', 'Pcs'),
                ('unit', 'Unit'),
                ('lot', 'LOT'), ],
        required=False, )
    supplier_ids = fields.Many2many(comodel_name='servismotor.supplier', string='Daftar Supplier')

