from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class order(models.Model):
    _name = 'servismotor.order'
    _description = 'New Description'

    servicedetail_ids = fields.One2many(
        comodel_name='servismotor.servicedetail', 
        inverse_name='orderk_id', 
        string='Servis')
    
    sparepartdetail_ids = fields.One2many(
        comodel_name='servismotor.sparepartdetail', 
        inverse_name='orders_id',
        string='sparepart')
    
    
    name = fields.Char(string='Kode Order', required=True)
    tanggal_datang = fields.Datetime(string ='Tanggal Kedatangan',default=fields.Datetime.now())
    tanggal_ambil = fields.Date(string='Tanggal Pengambilan', default=fields.Date.today())
    pemesan = fields.Many2one(
        comodel_name='res.partner', 
        string='Pemesan', 
        domain=[('is_pegawainya','=', True)],store=True)
    merek_motor = fields.Char(string='Merek Motor')
    mekanik_id = fields.Many2one(
        comodel_name='servismotor.mekanik',
        string='Mekanik',
        required=False)
        
    
    total = fields.Integer(compute='_compute_total', string='Total', store=True)

    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'),
                   ('done', 'Done'),
                   ('cancelled', 'Cancelled'),
                   ],
        required=True, readonly=True, default='draft')
    @api.depends('servicedetail_ids')
    def _compute_total(self):
        for record in self:
            a = sum(self.env['servismotor.servicedetail'].search([('orderk_id', '=', record.id)]).mapped('harga'))
            b = sum(self.env['servismotor.sparepartdetail'].search([('orders_id', '=', record.id)]).mapped('harga_jual'))
            record.total = a + b
    
    #sudah_ambil = fields.Boolean(string='Boleh Ambil', default=False)

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def unlink(self):
        if self.filtered(lambda line: line.state != 'draft'):
            raise UserError("Record bisa dihapus jika statusnya Draft")
        else:
            if self.sparepartdetail_ids:
                a = []
                for rec in self:
                    a = self.env['servismotor.sparepartdetail'].search([('orders_id', '=', rec.id)])
                    print(a)
                for ob in a:
                    print(str(ob.sparepart_id.name) + ' ' + str(ob.qty))
                    ob.sparepart_id.stok += ob.qty
        record = super(order, self).unlink()

    def write(self, vals):
        for rec in self:
            a = self.env['servismotor.sparepartdetail'].search([('orders_id', '=', rec.id)])
            print(a)
            for data in a:
                print(str(data.sparepart_id.name) + ' ' + str(data.qty))
                #data.sparepart_id.stok += data.qty
        record = super(order, self).write(vals)
        for rec in self:
            b = self.env['servismotor.sparepartdetail'].search([('orders_id', '=', rec.id)])
            print(a)
            print(b)
            for databaru in b:
                if databaru in a:
                    print(str(databaru.sparepart_id.name) + ' ' + str(databaru.qty) )
                    #databaru.sparepart_id.stok -= databaru.qty
                else:
                    pass
        return record

    sql_constraints = [
        ('no_nota_unik', 'unique (name)', 'Nomor Nota tidak boleh sama !!!')
    ]


class ServiceDetail(models.Model):
    _name = 'servismotor.servicedetail'
    _description = 'New Description'

    orderk_id = fields.Many2one(comodel_name='servismotor.order', string='Order Servis')
    
    servis_id = fields.Many2one(
        comodel_name='servismotor.servis', 
        string='Servis', 
        domain=[('stok','=','1')])
    
         
    name = fields.Char(string='Nama')
    harga = fields.Integer(compute='_compute_harga', string='Harga')
    qty = fields.Integer(string='Quantity')
    harga_satuan = fields.Integer(compute='_compute_harga_satuan', string='Biaya')

    @api.constrains('qty')
    def _check_stok(self):
        for record in self:
            bahan = self.env['servismotor.servis'].search([('stok', '<',record.qty),('id', '=',record.id)])
            if bahan:
                raise ValidationError("Stok sparepart tidak cukup")
    
    @api.depends('servis_id')
    def _compute_harga_satuan(self):
        for record in self:
            record.harga_satuan = record.servis_id.harga
    
    
    @api.depends('qty','harga_satuan')
    def _compute_harga(self):
        for record in self:
           record.harga = record.harga_satuan * record.qty
           
    @api.model
    def create(self,vals):
        record = super(ServiceDetail, self).create(vals) 
        if record.qty:
            self.env['servismotor.servis'].search([('id','=',record.servis_id.id)])
            return record


            
class sparepartDetail(models.Model):
    _name = 'servismotor.sparepartdetail'
    _description = 'New Description'
    
    orders_id = fields.Many2one(comodel_name='servismotor.order', string='Order sparepart')
    sparepart_id = fields.Many2one(
        comodel_name='servismotor.sparepart', 
        string='sparepart'
    )
    
    name = fields.Char(string='Name')
    harga_satuan = fields.Integer(compute='_compute_harga_satuan', string='Harga')
    
    @api.depends('sparepart_id')
    def _compute_harga_satuan(self):
        for record in self:
            record.harga_satuan = record.sparepart_id.harga_jual
    
    qty = fields.Integer(string='Quantity')
    
    @api.constrains('qty')
    def _check_stok(self):
        for rec in self:
            bahan = self.env['servismotor.sparepart'].search([('stok', '<',rec.qty),('id', '=',rec.id)])
            if bahan:
                raise ValidationError("Stok sparepart yang dipilih tidak cukup")
    
    harga_jual = fields.Integer(compute='_compute_harga', string='harga')
    
    @api.depends('harga_satuan','qty')
    def _compute_harga(self):
        for record in self:
               record.harga_jual = record.harga_satuan * record.qty
               
    
    @api.model
    def create(self, vals):
        record = super(sparepartDetail, self).create(vals)
        if record.qty:
            self.env['servismotor.sparepart'].search([('id', '=', record.sparepart_id.id)]).write(
                {'stok': record.sparepart_id.stok - record.qty})
        return record