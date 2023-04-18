from odoo import fields, models, api


class MedicineSaleOrder(models.Model):
    _name = 'hospital.sale.medicine'
    _description = 'Description'

    medicine_order_seq = fields.Char(
        string='Medicine_order_seq',
        required=True,
        copy=False,
        readonly=True,
        default='new')

    name = fields.Char()
    sale_date = fields.Datetime(
        string='Sale_date',
        required=False)
    quantity = fields.Integer(
        string='Quantity',
        required=False)

    medicine_name = fields.Many2one(
        comodel_name='hospital.medicine',
        string='Medicine_name',
        required=False)

    @api.model
    def create(self, vals_list):
        # print(vals_list)
        vals_list['medicine_order_seq'] = self.env['ir.sequence'].next_by_code('code.MO.seq')
        obj = super(MedicineSaleOrder, self).create(vals_list)
        # print(obj)
        return obj
