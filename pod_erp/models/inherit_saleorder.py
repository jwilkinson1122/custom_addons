# -*- coding: utf-8 -*-

from odoo import api, fields, models,_


class InheritedSaleOrder(models.Model):
    _inherit = 'sale.order'

    prescription_id = fields.Many2one('practitioner.prescription')
    # practitioner = fields.Char(related='prescription_id.practitioner.name')
    podiatrist = fields.Many2one('podiatry.practitioner', string='Podiatrist')
    prescription_date = fields.Date(related='prescription_id.checkup_date')
    purchase_order_count = fields.Char()
    po_ref = fields.Many2one('purchase.order', string='PO Ref')

    def print_prescription_report_ticket_size(self):
        return self.env.ref("pod_erp.practitioner_prescription_ticket_size2").report_action(self.prescription_id)

    def print_podiatry_prescription_report_ticket_size(self):
        return self.env.ref("pod_erp.practitioner_prescription_podiatry_ticket_size2").report_action(self.prescription_id)

    def _compute_amount_in_word(self):
        for rec in self:
                rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(string="This sale order is approved for the sum of: ", compute='_compute_amount_in_word')

    def print_sale_order_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "pod_erp.sale_order_report",
            'report_file': "pod_erp.sale_order_report",
            'report_type': 'qweb-pdf',
        }

    def print_purchase_order_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "pod_erp.purchase_order_report",
            'report_file': "pod_erp.purchase_order_report",
            'report_type': 'qweb-pdf',
        }

    @api.onchange('prescription_id')
    def test(self):
        product = self.env.ref('pod_erp.pod_erp_product')
        self.order_line = None
        if self.prescription_id.eye_examination_chargeable==True:
            self.order_line |= self.order_line.new({
                'name':'',
                'product_id':product.id,
                'product_uom_qty':1,
                'qty_delivered': 1,
                'product_uom':'',
                'price_unit':'',

            })



    # @api.model
    # def create(self,vals):
    #     order_line_product = [(0, 0, {'product_id':30,'partner_invoice_id':12,'partner_id':12})]
    #
    #     vals = {
    #
    #         'order_line': order_line_product,
    #
    #     }
    #     result = super(InheritedSaleOrder,self).create(vals)
    #     return result

    def print_podiatry_prescription_report(self):
        pass


    def print_prescription_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "pod_erp.sale_prescription_template",
            'report_file': "pod_erp.sale_prescription_template",
            'report_type': 'qweb-pdf'
        }













