from datetime import date

from odoo import api, fields, models

class ResPartner(models.Model):

    _inherit="res.partner"

    custom_total_due = fields.Monetary(
        string='Total Due',
        compute='_custom_compute_total_due',
        store=True,
        currency_field='currency_id'
    )

    custom_total_over_due = fields.Monetary(
        string='Total Overdue',
        compute='_custom_compute_total_over_due',
        store=True,
        currency_field='currency_id'  # Assuming currency_id is the field for currency
    )

    @api.depends('invoice_ids.amount_total', 'invoice_ids.state')
    def _custom_compute_total_due(self):
        for partner in self:
            total_due = 0.0
            # Filter for unpaid invoices (open and partially paid)
            unpaid_invoices = partner.invoice_ids.filtered(lambda inv: inv.state not in ['paid', 'cancel'])
            for inv in unpaid_invoices:
                total_due += inv.amount_residual  # Sum the residual amounts of unpaid invoices
            partner.custom_total_due = total_due

    @api.depends('invoice_ids.amount_total', 'invoice_ids.state', 'invoice_ids.invoice_date_due', 'invoice_ids.amount_residual')
    def _custom_compute_total_over_due(self):
        for partner in self:
            total_over_due = 0.0
            # Filter for invoices that are overdue and have a residual amount
            overdue_invoices = partner.invoice_ids.filtered(
                lambda inv: inv.state not in ['paid', 'cancel'] and inv.invoice_date_due and inv.invoice_date_due < date.today()
            )
            for inv in overdue_invoices:
                total_over_due += inv.amount_residual
            
            partner.custom_total_over_due = total_over_due
