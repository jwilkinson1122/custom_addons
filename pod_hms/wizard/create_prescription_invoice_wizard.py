# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import Warning

# class podiatry_rx_invoice(models.TransientModel):

#     _name = 'podiatry.rx.invoice'
#     _description = 'podiatry rx invoice'

#     def create_rx_invoice(self):
#         if self._context == None:
#             self._context = {}
#         active_ids = self._context.get('active_ids')
#         list_of_ids = []
#         rx_req_obj = self.env['podiatry.patient.rx']


class create_prescription_invoice(models.TransientModel):
    _name = 'create.prescription.invoice'
    _description = 'Create Prescrition invoice'

    def create_prescription_invoice(self):
        active_ids = self._context.get('active_ids')
        active_ids = active_ids or False
        rx_req_obj = self.env['podiatry.prescription.order']
        account_invoice_obj = self.env['account.move']
        account_invoice_line_obj = self.env['account.move.line']
        ir_property_obj = self.env['ir.property']
        inv_list = []
        rx_reqs = rx_req_obj.browse(active_ids)
        for rx_req in rx_reqs:
            if len(rx_req.prescription_line_ids) < 1:
                raise Warning('At least one prescription line is required.')

            if rx_req.is_invoiced == True:
                raise Warning('All ready Invoiced.')
            sale_journals = self.env['account.journal'].search(
                [('type', '=', 'sale')])
            invoice_vals = {
                'name': self.env['ir.sequence'].next_by_code('pres_inv_seq'),
                'invoice_origin': rx_req.name or '',
                'move_type': 'out_invoice',
                'ref': False,
                'partner_id': rx_req.patient_id.patient_id.id,
                'invoice_date': date.today(),
                'partner_shipping_id': rx_req.patient_id.patient_id.id,
                'currency_id': rx_req.patient_id.patient_id.currency_id.id,
                'invoice_payment_term_id': False,
                'fiscal_position_id': rx_req.patient_id.patient_id.property_account_position_id.id,
                'team_id': False,
                'company_id': rx_req.patient_id.patient_id.company_id.id or False,
            }

            res = account_invoice_obj.create(invoice_vals)
            list_of_vals = []
            for p_line in rx_req.prescription_line_ids:

                invoice_line_account_id = False
                if p_line.treatment_id.product_id.id:
                    invoice_line_account_id = p_line.treatment_id.product_id.property_account_income_id.id or p_line.treatment_id.product_id.categ_id.property_account_income_categ_id.id or False
                if not invoice_line_account_id:
                    invoice_line_account_id = ir_property_obj.get(
                        'property_account_income_categ_id', 'product.category')
                if not invoice_line_account_id:
                    raise UserError(
                        _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                        (p_line.treatment_id.product_id.name,))

                tax_ids = []
                taxes = p_line.treatment_id.product_id.taxes_id.filtered(
                    lambda r: not p_line.treatment_id.product_id.company_id or r.company_id == p_line.treatment_id.product_id.company_id)
                tax_ids = taxes.ids

                invoice_line_vals = {
                    'name': p_line.treatment_id.product_id.display_name or '',
                    'move_name': p_line.name or '',
                    'account_id': invoice_line_account_id,
                    'price_unit': p_line.treatment_id.product_id.lst_price,
                    'product_uom_id': p_line.treatment_id.product_id.uom_id.id,
                    'quantity': 1,
                    'product_id': p_line.treatment_id.product_id.id,
                }
                list_of_vals.append((0, 0, invoice_line_vals))

            res1 = res.write({'invoice_line_ids': list_of_vals})

            inv_list.append(res.id)
            if res:
                imd = self.env['ir.model.data']
                rx_reqs.write({'is_invoiced': True})
                action = self.env.ref('account.action_move_out_invoice_type')
                list_view_id = imd._xmlid_to_res_id(
                    'account.view_invoice_tree')
                form_view_id = imd._xmlid_to_res_id('account.view_move_form')
                result = {

                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [(list_view_id, 'tree'), (form_view_id, 'form')],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,
                }

                if res:
                    result['domain'] = "[('id','in',%s)]" % inv_list
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
