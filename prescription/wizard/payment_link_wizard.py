# -*- coding: utf-8 -*-


from werkzeug import urls

from odoo import _, api, fields, models
from odoo.tools import format_amount


class PaymentLinkWizard(models.TransientModel):
    _inherit = 'payment.link.wizard'
    _description = 'Generate Prescription Payment Link'

    amount_paid = fields.Monetary(string="Already Paid", readonly=True)
    confirmation_message = fields.Char(compute='_compute_confirmation_message')

    @api.depends('amount')
    def _compute_confirmation_message(self):
        self.confirmation_message = False
        for wizard in self.filtered(lambda w: w.res_model == 'prescription'):
            prescription = wizard.env['prescription'].sudo().browse(wizard.res_id)
            if prescription.state in ('draft', 'sent') and prescription.require_payment:
                remaining_amount = prescription._get_prepayment_required_amount() - prescription.amount_paid
                if wizard.currency_id.compare_amounts(wizard.amount, remaining_amount) >= 0:
                    wizard.confirmation_message = _("This payment will confirm the quotation.")
                else:
                    wizard.confirmation_message = _(
                        "Customer needs to pay at least %(amount)s to confirm the order.",
                        amount=format_amount(wizard.env, remaining_amount, wizard.currency_id),
                    )

    def _get_additional_link_values(self):
        """ Override of `payment` to add `prescription_id` to the payment link values.

        The other values related to the prescription order are directly read from the prescription order.

        Note: self.ensure_one()

        :return: The additional payment link values.
        :rtype: dict
        """
        res = super()._get_additional_link_values()
        if self.res_model != 'prescription':
            return res

        # Order-related fields are retrieved in the controller
        return {
            'prescription_id': self.res_id,
        }
