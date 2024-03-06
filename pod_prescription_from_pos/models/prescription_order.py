from odoo import _, api, fields, models
import datetime


class PrescriptionOrder(models.Model):
    _inherit = 'prescription.order'

    is_pos_created = fields.Boolean(string='Create from POS')


    @api.model
    def create_prescription_from_pos(self, oderdetails):
        vals = {}
        order_id = self.env['prescription.order'].create({
            'partner_id': oderdetails.get('partner_id'),
            'date_order': datetime.date.today(),
            'is_pos_created': True,
            'state': 'draft',
            'amount_tax': oderdetails.get('tax_amount'),
            })
        vals['name'] = order_id.name
        vals['id'] = order_id.id
        for data in oderdetails:
            if not data == 'partner_id' and not data == 'tax_amount':
                current_dict = oderdetails.get(data)
                order_id.order_line = [(0, 0, {
                    'product_id': current_dict.get('product'),
                    'product_uom_qty':  current_dict.get('quantity'),
                    'price_unit': current_dict.get('price'),
                    'discount': current_dict.get('discount'),
                })]
        return vals