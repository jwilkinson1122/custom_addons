from odoo import http, models, fields
from odoo.http import request
import json

class Servismotor(http.Controller):
    @http.route('/servismotor/getsparepart', auth='public', method=['GET'])
    def getsparepart(self, **kw):
        sparepart = self.env['servismotor.sparepart'].search([])
        isi = []
        for b in sparepart:
            isi.append({
                'nama_sparepart' : b.name,
                'hrg_jual' : b.hrg_jual,
                'stok' : b.stok
            })
        return json.dumps(isi)
    
    @http.route('/servismotor/getsupplier', auth='public', method=['GET'])
    def getsupplier(self, **kw):
        supplier = request.env['servismotor.sparepart'].search([])
        pem = []
        for p in supplier:
            pem.append({
                'nama_perusahaan' : p.name,
                'alamat' : p.alamat,
                'no_telepon' : p.no_pic,
            })
        return json.dumps(pem)