# -*- coding: utf-8 -*-


from odoo import fields, models


class StockWarnInsufficientQtyPrescription(models.TransientModel):
    _name = 'stock.warn.insufficient.qty.prescription'
    _inherit = 'stock.warn.insufficient.qty'
    _description = 'Warn Insufficient Prescription Quantity'

    prescription_id = fields.Many2one('prescription.order', string='Prescription')

    def _get_reference_document_company_id(self):
        return self.prescription_id.company_id

    def action_done(self):
        self.ensure_one()
        return self.prescription_id._action_prescription_confirm()
