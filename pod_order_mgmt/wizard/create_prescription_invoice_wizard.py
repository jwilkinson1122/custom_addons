# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import UserError
from datetime import date

class CreatePrescriptionInvoice(models.TransientModel):
    _name = 'create.prescription.invoice'
    _description = 'Create Prescription invoice'

    def _get_invoice_line_account(self, p_line):
        """Fetch the account ID for the invoice line."""
        if p_line.product_id.id:
            return p_line.product_id.property_account_income_id.id or \
                   p_line.product_id.categ_id.property_account_income_categ_id.id
        account_id = self.env['ir.property'].get('property_account_income_categ_id', 'product.category')
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                p_line.product_id.name)
        return account_id

    def _create_invoice_lines(self, prescription_req):
        """Prepare the invoice lines."""
        list_of_vals = []
        for p_line in prescription_req.prescription_order_lines:
            account_id = self._get_invoice_line_account(p_line)
            taxes = p_line.product_id.taxes_id.filtered(
                lambda r: not p_line.product_id.company_id or r.company_id == p_line.product_id.company_id)
            
            invoice_line_vals = {
                'name': p_line.product_id.display_name or '',
                'move_name': p_line.name or '',
                'account_id': account_id,
                'price_unit': p_line.product_id.lst_price,
                'product_uom_id': p_line.product_id.uom_id.id,
                'quantity': 1,
                'product_id': p_line.product_id.id,
                'tax_ids': [(6, 0, taxes.ids)],
            }
            list_of_vals.append((0, 0, invoice_line_vals))
        return list_of_vals

    def create_prescription_invoice(self):
        active_ids = self._context.get('active_ids', [])
        prescription_reqs = self.env['pod.prescription.order'].browse(active_ids)
        inv_list = []

        for prescription_req in prescription_reqs:
            if not prescription_req.prescription_order_lines:
                raise UserError('At least one prescription line is required.')
            if prescription_req.is_invoiced:
                raise UserError('Already Invoiced.')
            # patient = prescription_req.patient_id.patient_id
            practice = prescription_req.practice_id.practice_id
            invoice_vals = {
                'name': self.env['ir.sequence'].next_by_code('pres_inv_seq'),
                'invoice_origin': prescription_req.name or '',
                'move_type': 'out_invoice',
                #     'partner_id': patient.id,
                'partner_id': practice.id,
                'invoice_date': date.today(),
                'partner_shipping_id': practice.id,
                'currency_id': practice.currency_id.id,
                'fiscal_position_id': practice.property_account_position_id.id,
                'company_id': practice.company_id.id or False,
            }

            invoice = self.env['account.move'].create(invoice_vals)
            invoice_lines = self._create_invoice_lines(prescription_req)
            invoice.write({'invoice_line_ids': invoice_lines})

            inv_list.append(invoice.id)
            prescription_req.write({'is_invoiced': True})

        action = self.env.ref('account.action_move_out_invoice_type')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [(view.view_id.id, view.view_mode) for view in action.view_id],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
            'domain': [('id', 'in', inv_list)],
        }
        return result

# from msilib.schema import Error
# from odoo import api, fields, models, _
# from datetime import date, datetime
# from odoo.exceptions import Warning


# class create_prescription_invoice(models.TransientModel):
#     _name = 'create.prescription.invoice'
#     _description = 'Create Prescrition invoice'

#     def create_prescription_invoice(self):
#         active_ids = self._context.get('active_ids')
#         active_ids = active_ids or False
#         prescription_req_obj = self.env['pod.prescription.order']
#         account_invoice_obj = self.env['account.move']
#         account_invoice_line_obj = self.env['account.move.line']
#         ir_property_obj = self.env['ir.property']
#         inv_list = []
#         prescription_reqs = prescription_req_obj.browse(active_ids)
#         for prescription_req in prescription_reqs:
#             if len(prescription_req.prescription_order_lines) < 1:
#                 raise Warning('At least one prescription line is required.')

#             if prescription_req.is_invoiced == True:
#                 raise Warning('All ready Invoiced.')
#             sale_journals = self.env['account.journal'].search(
#                 [('type', '=', 'sale')])
#             invoice_vals = {
#                 'name': self.env['ir.sequence'].next_by_code('pres_inv_seq'),
#                 'invoice_origin': prescription_req.name or '',
#                 'move_type': 'out_invoice',
#                 'ref': False,
#                 'partner_id': prescription_req.patient_id.patient_id.id,
#                 'invoice_date': date.today(),
#                 'partner_shipping_id': prescription_req.patient_id.patient_id.id,
#                 'currency_id': prescription_req.patient_id.patient_id.currency_id.id,
#                 'invoice_payment_term_id': False,
#                 'fiscal_position_id': prescription_req.patient_id.patient_id.property_account_position_id.id,
#                 'team_id': False,
#                 'company_id': prescription_req.patient_id.patient_id.company_id.id or False,
#             }

#             res = account_invoice_obj.create(invoice_vals)
#             list_of_vals = []
#             for p_line in prescription_req.prescription_order_lines:

#                 invoice_line_account_id = False
#                 if p_line.product_id.id:
#                     invoice_line_account_id = p_line.product_id.property_account_income_id.id or p_line.product_id.categ_id.property_account_income_categ_id.id or False
#                 if not invoice_line_account_id:
#                     invoice_line_account_id = ir_property_obj.get(
#                         'property_account_income_categ_id', 'product.category')
#                 if not invoice_line_account_id:
#                     raise Error(
#                         _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
#                         (p_line.product_id.name,))

#                 tax_ids = []
#                 taxes = p_line.product_id.taxes_id.filtered(
#                     lambda r: not p_line.product_id.company_id or r.company_id == p_line.product_id.company_id)
#                 tax_ids = taxes.ids

#                 invoice_line_vals = {
#                     'name': p_line.product_id.display_name or '',
#                     'move_name': p_line.name or '',
#                     'account_id': invoice_line_account_id,
#                     'price_unit': p_line.product_id.lst_price,
#                     'product_uom_id': p_line.product_id.uom_id.id,
#                     'quantity': 1,
#                     'product_id': p_line.product_id.id,
#                 }
#                 list_of_vals.append((0, 0, invoice_line_vals))

#             res1 = res.write({'invoice_line_ids': list_of_vals})

#             inv_list.append(res.id)
#             if res:
#                 imd = self.env['ir.model.data']
#                 prescription_reqs.write({'is_invoiced': True})
#                 action = self.env.ref('account.action_move_out_invoice_type')
#                 list_view_id = imd._xmlid_to_res_id(
#                     'account.view_invoice_tree')
#                 form_view_id = imd._xmlid_to_res_id('account.view_move_form')
#                 result = {

#                     'name': action.name,
#                     'help': action.help,
#                     'type': action.type,
#                     'views': [(list_view_id, 'tree'), (form_view_id, 'form')],
#                     'target': action.target,
#                     'context': action.context,
#                     'res_model': action.res_model,
#                 }

#                 if res:
#                     result['domain'] = "[('id','in',%s)]" % inv_list
#         return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
