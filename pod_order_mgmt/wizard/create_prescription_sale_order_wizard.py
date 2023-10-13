# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import Warning

    # def create_sale_order(self):
    #     sale_order = self.env['sale.order'].search([('prescription_order_id', '=', self.id)], limit=1)
 
    #     if sale_order:
    #         return self._prepare_action(_('Prescription order'), 'sale.order', sale_order.id)
        
    #     vals = {
    #         'prescription_order_id': self.id,
    #         'partner_id': self.practice_id.id,
    #         'practitioner_id': self.practitioner_id.id,
    #         'patient_id': self.patient_id.id,
    #     }
        
    #     new_sale_order = self.env['sale.order'].create(vals)
        
    #     for line in self.prescription_order_lines:
    #         line_vals = {
    #             'order_id': new_sale_order.id,
    #             'product_id': line.product_id.id,
    #             'name': line.product_id.name,
    #             'product_uom': line.product_id.uom_id.id,
    #             'product_uom_qty': line.quantity,
    #             'price_unit': line.product_id.lst_price,  
          
    #         }
    #         self.env['sale.order.line'].create(line_vals)
            
    #     return self._prepare_action(_('Prescription Order'), 'sale.order', new_sale_order.id)

    # def _prepare_action(self, name, res_model, res_id=None, context=None):
    #     action = {
    #         'name': name,
    #         'view_type': 'form',
    #         'res_model': res_model,
    #         'view_id': False,
    #         'view_mode': 'form',
    #         'type': 'ir.actions.act_window',
    #     }
    #     if res_id:
    #         action['res_id'] = res_id
    #     if context:
    #         action['context'] = context
    #     return action



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
        
        if prescription_record.prescription_order_lines:
            for p_line in prescription_record.prescription_order_lines:

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
