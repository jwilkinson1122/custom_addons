from tokenize import Name
from odoo import fields, models, api


class pembelian(models.Model):
    _name = 'servismotor.pembelian'
    _description = 'Description'

    name = fields.Char(string='No. Nota')

    tgl_nota = fields.Datetime(
        string='Tanggal Nota',
        required=False,
        default=fields.Datetime.now())

    kode_supplier= fields.Many2one(
        comodel_name='servismotor.supplier',
        string='kode_Pemasok',
        required=False)

    total = fields.Integer(
        compute='_compute_total',
        string='Total',
        required=False)
    
    detailpembelian_ids = fields.One2many(
        comodel_name='servismotor.pembeliandetail', 
        inverse_name='pembelian_id', 
        string='List sparepart')


    @api.depends('detailpembelian_ids')
    def _compute_total(self):
        for record in self:
            a = sum(self.env['servismotor.pembeliandetail'].search(
                [('pembelian_id', '=', record.id)]).mapped('subtotal'))
            record.total = a

class pembeliandetail(models.Model):
    _name = 'servismotor.pembeliandetail'
    _description = 'Description'
    #_rec_name = 'kode_pemasok'

    name = fields.Char(
        string='No_masuk')

    sparepart_id = fields.Many2one(
        comodel_name='servismotor.sparepart',
        string='Kode_sparepart_Ids',
        required=False)

    harga_satuan = fields.Integer(
        compute="_compute_hargasatuan",
        string='Harga_satuan',
        required=False)

    qty = fields.Integer(
        string='qty',
        required=False)

    subtotal = fields.Integer(
        compute="_compute_subtotal",
        string='SubTotal',
        required=False)

    pembelian_id = fields.Many2one(
        comodel_name='servismotor.pembelian',
        string='No_pembelian',
        required=False)
    
    satuan = fields.Char(
        compute='_compute_satuan', 
        string='satuan')

    @api.depends('sparepart_id')
    def _compute_satuan(self):
        for record in self:
            record.satuan = record.sparepart_id.satuan

    @api.model
    def create(self, vals):
        record = super(pembeliandetail, self).create(vals)
        if record.qty:
            self.env['servismotor.sparepart'].search([('id', '=', record.sparepart_id.id)]).write({
                'stok': record.sparepart_id.stok+record.qty})
            return record

    @api.depends('sparepart_id')
    def _compute_hargasatuan(self):
        for a in self:
            a.harga_satuan = a.sparepart_id.harga_beli

    @api.depends('qty','harga_satuan')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.qty * record.harga_satuan