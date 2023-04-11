# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import Warning


class create_prescription_shipment(models.TransientModel):
    _name = 'create.prescription.shipment'
    _description = 'Create Prescription Shipment'

    def create_prescription_shipment(self):
        active_id = self._context.get('active_id')
        prescription_obj = self.env['podiatry.prescription']
        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']

        prescription_record = prescription_obj.browse(active_id)
        if prescription_record.is_shipped == True:
            raise Warning('All ready shipped.')

        res = sale_order_obj.create({'partner_id': prescription_record.practitioner_id.id})
        
        if prescription_record.prescription_device_lines:
            for p_line in prescription_record.prescription_device_lines:

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
