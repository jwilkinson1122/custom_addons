from odoo import fields, models, api


class supplier(models.Model):
    _name = 'servismotor.supplier'
    _description = 'Description'

    name = fields.Char(
        string='Nama Supplier',
        required=False)
#    kode_pemasok = fields.Char(
#        string='Kode_Pemasok',
#        required=False)

#    kode_pembelian_ids = fields.One2many(
#        comodel_name='fikrishop.pembelian',
#        inverse_name='kode_pemasok',
#        string='Kode_Pembelian_ids',
#        required=False)

    alamat = fields.Char(
        string='Alamat Supplier',
        required=False)

#    kota = fields.Char(
#        string='Kota',
#        required=False)

#    provinsi = fields.Char(
#        string='Provinsi',
#        required=False)

    pic = fields.Char(
        string='PIC',
        required=False)

    no_pic = fields.Char(
        string='No.Telepon',
        required=False)
    
    sparepart_ids = fields.Many2many(
        comodel_name='servismotor.sparepart', 
        string='Supply Sparepart')