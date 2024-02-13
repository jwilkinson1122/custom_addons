# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import Warning


class CreatePrescriptionSaleOrder(models.TransientModel):
    _name = 'create.prescription.sale.order'
    _description = 'Create Prescription Sale Order'

    def create_prescription_sale_order(self):
        active_id = self._context.get('active_id')
        prescription_obj = self.env['pod.prescription.order']
        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']

        prescription_record = prescription_obj.browse(active_id)
        if prescription_record.is_confirmed == True:
            raise Warning('A sales order already has been confirmed for the prescription.')

        vals = sale_order_obj.create({
            'practice_id': prescription_record.practice_id.id,
            'partner_id': prescription_record.practitioner_id.id,
            'patient_id': prescription_record.patient_id.id,
                                     })
        
        if prescription_record.order_line:
            for p_line in prescription_record.order_line:

                res1 = sale_order_line_obj.create({'product_id': p_line.product_id.id,
                                                   'product_uom': p_line.product_id.uom_id.id,
                                                   'name': p_line.product_id.name,
                                                   'product_uom_qty': 1,
                                                   'price_unit': p_line.product_id.lst_price,
                                                   'order_id': vals.id})
        else:
            raise Warning('There is no order line.')
        prescription_record.write({'is_ordered': True})
        vals.action_confirm()
        result = vals.action_view_delivery()
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
