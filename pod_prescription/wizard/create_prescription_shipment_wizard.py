# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import Warning


class CreatePrescriptionShipment(models.TransientModel):
    _name = 'create.prescription.shipment'
    _description = 'Create Prescription Shipment'

    def create_prescription_shipment(self):
        active_id = self._context.get('active_id')
        prescription_obj = self.env['pod.prescription.order']
        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']

        prescription_record = prescription_obj.browse(active_id)
        if prescription_record.is_shipped == True:
            raise Warning('All ready shipped.')

        res = sale_order_obj.create({
            'partner_id': prescription_record.practice_id.id,
            'practitioner_id': prescription_record.practitioner_id.id,
            'patient_id': prescription_record.patient_id.id,
                                     })
        
        #  vals = {
        #     'prescription_order_id': self.id,
        #     'partner_id': self.practice_id.id,
        #     'practitioner_id': self.practitioner_id.id,
        #     'patient_id': self.patient_id.id,
        #     'invoice_status': 'to_invoice',  # Setting the invoice_status to 'to_invoice'
        # }
        
        if prescription_record.order_line:
            for p_line in prescription_record.order_line:

                res1 = sale_order_line_obj.create({'product_id': p_line.product_id.id,
                                                   'product_uom': p_line.product_id.uom_id.id,
                                                   'name': p_line.product_id.name,
                                                   'product_uom_qty': 1,
                                                   'price_unit': p_line.product_id.lst_price,
                                                   'order_id': res.id})
        else:
            raise Warning('There is no shipment line.')
        prescription_record.write({'is_shipped': True})
        res.action_confirm()
        result = res.action_view_delivery()
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



# class CreatePrescriptionShipment(models.TransientModel):
#     _name = 'create.prescription.shipment'
#     _description = 'Create Prescription Shipment'

#     def create_prescription_shipment(self):
#         prescription = self.env['pod.prescription.order'].browse(self._context.get('active_id'))

#         if prescription.is_shipped:
#             raise UserError(_('Already shipped.'))

#         sale_order = self.env['sale.order'].create({
#             'partner_id': prescription.practice_id.id,
#             'practitioner_id': prescription.practitioner_id.id,
#             'patient_id': prescription.patient_id.id,
#         })

#         if not prescription.order_line:
#             raise UserError(_('There is no shipment line.'))

#         for line in prescription.order_line:
#             self.env['sale.order.line'].create({
#                 'product_id': line.product_id.id,
#                 'product_uom': line.product_id.uom_id.id,
#                 'name': line.product_id.name,
#                 'product_uom_qty': 1,
#                 'price_unit': line.product_id.lst_price,
#                 'order_id': sale_order.id,
#             })

#         prescription.write({'is_shipped': True})
#         sale_order.action_confirm()
#         return sale_order.action_view_delivery()


