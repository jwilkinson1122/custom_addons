from odoo import models, fields, api


class practice_request_invoices(models.Model):
    _inherit = 'account.move'

    is_practice_invoice = fields.Boolean(string="Is Practice Invoice")
    practice_request = fields.Many2one()
    # 'practice.appointment', string="Practice Appointment", help="Source Document")

    def action_invoice_paid(self):
        res = super(practice_request_invoices, self).action_invoice_paid()

        return res
