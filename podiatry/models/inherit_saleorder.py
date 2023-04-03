# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class InheritedSaleOrder(models.Model):
    _inherit = 'sale.order'

    prescription_id = fields.Many2one('podiatry.prescription', readonly=True) 
    practice_id = fields.Char(related='prescription_id.practice_id.name')
    practitioner_id = fields.Char(
        related='prescription_id.practitioner_id.name')
    patient_id = fields.Char(related='prescription_id.patient_id.name')
    prescription_date = fields.Date(
        related='prescription_id.prescription_date')
    purchase_order_count = fields.Char()
    po_ref = fields.Many2one('purchase.order', string='PO Ref')

    def print_prescription_report_ticket_size(self):
        return self.env.ref("podiatry.practitioner_prescription_ticket_size2").report_action(self.prescription_id)

    def print_podiatry_prescription_report_ticket_size(self):
        return self.env.ref("podiatry.practitioner_prescription_podiatry_ticket_size2").report_action(self.prescription_id)

    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(
                rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(
        string="This sale order is approved for the sum of: ", compute='_compute_amount_in_word')

    def print_sale_order_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "podiatry.sale_order_report",
            'report_file': "podiatry.sale_order_report",
            'report_type': 'qweb-pdf',
        }

    def print_prescription_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "podiatry.sale_prescription_template",
            'report_file': "podiatry.sale_prescription_template",
            'report_type': 'qweb-pdf'
        }

    def print_prescription_report(self):
        pass

    def print_prescription_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "podiatry.sale_prescription_template",
            'report_file': "podiatry.sale_prescription_template",
            'report_type': 'qweb-pdf'
        }


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _prepare_from_pos(self, sale_order, order_line_data):
        ProductProduct = self.env["product.product"]
        product = ProductProduct.browse(order_line_data["product_id"])
        return {
            "order_id": sale_order.id,
            "product_id": order_line_data["product_id"],
            "name": product.name,
            "product_uom_qty": order_line_data["qty"],
            "discount": order_line_data["discount"],
            "price_unit": order_line_data["price_unit"],
            "tax_id": order_line_data["tax_ids"],
        }


