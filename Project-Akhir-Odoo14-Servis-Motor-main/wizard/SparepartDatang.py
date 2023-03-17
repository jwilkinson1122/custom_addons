from odoo import api, fields, models

class SparepartDatang(models.TransientModel):
    _name = 'servismotor.sparepartdatang'

    sparepart_id = fields.Many2one(
        comodel_name='servismotor.sparepart',
        string='Nama Sparepart',
        required=True)

    jumlah = fields.Integer(
        string='Jumlah',
        required=False)

    def sparepart_datang(self):
        for rec in self:
            self.env['servismotor.sparepart']\
                .search([('id', '=', rec.sparepart_id.id)])\
                .write({'stok': rec.sparepart_id.stok + rec.jumlah})

