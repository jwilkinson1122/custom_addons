# # -*- coding: utf-8 -*-
# # See LICENSE file for full copyright and licensing details.

# from odoo import api, fields, models
# from odoo.exceptions import Warning
# from datetime import date, datetime

# class pod_order_shipment_wizard(models.TransientModel):
#     _name = 'pod.order.shipment'
#     _description = 'Create Order Shipment'

#     def pod_order_shipment(self):
#         active_id = self._context.get('active_id')
#         pod_order_obj = self.env['pod.order']
#         sale_order_obj = self.env['sale.order']
#         sale_oder_detail_obj = self.env['sale.order.line']

#         pod_order_record = pod_order_obj.browse(active_id)
#         if pod_order_record.is_shipped == True:
#             raise Warning('All ready shipped.')

#         res = sale_order_obj.create({'partner_id': pod_order_record.pod_patient_id.pod_patient_id.id,
#                                      })
#         if pod_order_record.pod_oder_detail_ids:
#             for p_line in pod_order_record.pod_oder_detail_ids:
#                 res1 = sale_oder_detail_obj.create({'product_id': p_line.product_id.id,
#                                                    'product_uom': p_line.product_id.uom_id.id,
#                                                    'name': p_line.product_id.name,
#                                                    'product_uom_qty': 1,
#                                                    'price_unit': p_line.product_id.lst_price,
#                                                    'order_id': res.id})
#         else:
#             raise Warning('There is no shipment line.')
#         pod_order_record.write({'is_shipped': True})
#         res.action_confirm()
#         result = res.action_view_delivery()
#         return result
