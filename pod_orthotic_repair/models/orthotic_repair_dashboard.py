# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api
from datetime import timedelta, datetime


class OrthoticRepairDashboard(models.Model):
    """Orthotic Repair Dashboard"""
    _name = "orthotic.repair.dashboard"
    _description = __doc__

    @api.model
    def get_orthotic_repair_dashboard(self):
        total_repair_orders = self.env['orthotic.repair.order'].sudo().search_count([])
        assign_to_technician = self.env['orthotic.repair.order'].sudo().search_count(
            [('stages', '=', 'assign_to_technician')])
        orthotic_inspection_mode = self.env['orthotic.repair.order'].sudo().search_count(
            [('stages', '=', 'inspection_mode')])
        in_progress_orders = self.env['orthotic.repair.order'].sudo().search_count([('stages', '=', 'in_progress')])
        review_orders = self.env['orthotic.repair.order'].sudo().search_count([('stages', '=', 'review')])
        complete_orders = self.env['orthotic.repair.order'].sudo().search_count([('stages', '=', 'complete')])
        cancel_orders = self.env['orthotic.repair.order'].sudo().search_count([('stages', '=', 'cancel')])

        repair_orders_details = [['Repair Orders', 'Assign to Technicians', 'Inspection Mode', 'In Progress',
                                  'In Review', 'Completed', 'Cancelled'],
                                 [total_repair_orders, assign_to_technician, orthotic_inspection_mode,
                                  in_progress_orders, review_orders, complete_orders, cancel_orders]]

        data = {
            'total_repair_orders': total_repair_orders,
            'assign_to_technician': assign_to_technician,
            'orthotic_inspection_mode': orthotic_inspection_mode,
            'in_progress_orders': in_progress_orders,
            'review_orders': review_orders,
            'complete_orders': complete_orders,
            'cancel_orders': cancel_orders,
            'repair_orders_details': repair_orders_details,
            'top_five_repair_services': self.get_top_five_repair_services(),
            'orthotic_repair_duration': self.get_repair_time_period(),
            'repair_order_month': self.get_repair_month(),
            'invoice_status': self.get_invoice_due_paid_status(),
        }
        return data

    def get_top_five_repair_services(self):
        repair_service = {}
        for group in self.env['orthotic.repair.service'].read_group([], ['product_id'], ['product_id'],
                                                                   orderby="product_id DESC", limit=5):
            service_name = self.env['product.product'].sudo().browse(int(group['product_id'][0])).name
            repair_service[service_name] = group['product_id_count']
        repair_service = dict(sorted(repair_service.items(), key=lambda item: item[1], reverse=True))
        return [list(repair_service.keys()), list(repair_service.values())]

    def get_repair_time_period(self):
        repair_data = []
        mor_id = self.env['orthotic.repair.order'].search([])
        for data in mor_id:
            repair_data.append({
                'orthotic_problem': data.orthotic_problem,
                'receiving_date': str(data.receiving_date),
                'delivery_date': str(data.delivery_date),
            })
        return repair_data

    def get_repair_month(self):
        year = fields.date.today().year
        data_dict = {'January': 0,
                     'February': 0,
                     'March': 0,
                     'April': 0,
                     'May': 0,
                     'June': 0,
                     'July': 0,
                     'August': 0,
                     'September': 0,
                     'October': 0,
                     'November': 0,
                     'December': 0,
                     }
        order = self.env['orthotic.repair.order'].search([])
        for data in order:
            if data.receiving_date.year == year:
                if data.stages == 'complete':
                    data_dict[data.receiving_date.strftime(
                        "%B")] = data_dict[
                                     data.receiving_date.strftime("%B")] + data.order_amount
        return [list(data_dict.keys()), list(data_dict.values())]

    def get_invoice_due_paid_status(self):
        repair_data = {}
        paid_amount = 0.0
        not_paid_amount = 0.0

        invoice_id = self.env['account.move'].sudo().search([('orthotic_repair_order_id', '!=', False)])
        for rec in invoice_id:
            if rec.payment_state == 'paid':
                paid_amount = paid_amount + rec.amount_total
            else:
                not_paid_amount = not_paid_amount + rec.amount_total
        repair_data['Amount Paid'] = paid_amount
        repair_data['Amount Due'] = not_paid_amount
        return [list(repair_data.keys()), list(repair_data.values())]
