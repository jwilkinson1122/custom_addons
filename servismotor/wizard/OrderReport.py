from odoo import fields, models, api


class OrderReport(models.TransientModel):
    _name = 'servismotor.orderreport'
    _description = 'Description'

    pemesan = fields.Many2one(
        comodel_name='res.partner',
        string='Pemesan',
        required=False)
    tgl_datang = fields.Date(
        string='Tanggal Datang',
        required=False)
    tgl_ambil = fields.Date(
        string='Tanggal Ambil',
        required=False)

    def action_order_report(self):
        filter = []
        pemesan = self.pemesan
        tgl_datang = self.tgl_datang
        tgl_ambil = self.tgl_ambil
        if pemesan:
            filter += [('pemesan', '=', pemesan.id)]
        if tgl_datang:
            filter += [('tanggal_datang', '=', tgl_datang)]
        if tgl_ambil:
            filter += [('tanggal_ambil', '=', tgl_ambil)]
        print(filter)
        order = self.env['servismotor.order'].search_read(filter)
        print(order)
        data = {
            'form': self.read()[0],
            'orderxx': order,
        }
        print(data)
        return self.env.ref('servismotor.wizard_orderreport_pdf').report_action(self, data=data)
