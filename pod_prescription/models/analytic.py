# -*- coding: utf-8 -*-


from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    allowed_rx_line_ids = fields.Many2many('prescription.order.line', compute='_compute_allowed_rx_line_ids')
    rx_line = fields.Many2one('prescription.order.line', string='Prescription Order Item', domain="[('id', 'in', allowed_rx_line_ids)]")

    def _default_prescription_line_domain(self):
        """ This is only used for delivered quantity of RX line based on analytic line, and timesheet
            (see prescription_timesheet). This can be override to allow further customization.
        """
        self.ensure_one()
        return [('qty_delivered_method', '=', 'analytic')]

    def _compute_allowed_rx_line_ids(self):
        for timesheet in self:
            domain = timesheet._default_prescription_line_domain()
            timesheet.allowed_rx_line_ids = self.env['prescription.order.line'].search(domain)


class AccountAnalyticApplicability(models.Model):
    _inherit = 'account.analytic.applicability'
    _description = "Analytic Plan's Applicabilities"

    business_domain = fields.Selection(
        selection_add=[
            ('prescription_order', 'Prescription Order'),
        ],
        ondelete={'prescription_order': 'cascade'},
    )
