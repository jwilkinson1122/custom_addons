from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'servismotor.mekanik'
    _description = 'Description'

    name = fields.Char(
        string='Nama',
        required=True
    )

    id_mekanik = fields.Char(
        string='ID Pegawai',
        required=False)

    status_pegawai = fields.Selection([
        ('kontrak', 'Kontrak'),
        ('tetap', 'Pegawai Tetap'),
        ('magang', 'Pegawai Magang')], string='status_pegawai')

    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female')],
                              string='Gender',
                              required='True')

    alamat = fields.Char(string='Alamat')

    no_telepon = fields.Char(  # np_tlpn
        string='No telepon',  # np_tlpn
        required=False)
