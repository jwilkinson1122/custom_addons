

import base64

from odoo import _, api, Command, models
from odoo.tools import file_open


class OnboardingStep(models.Model):
    _inherit = 'onboarding.onboarding.step'

    @api.model
    def action_open_step_prescriptions_order_confirmation(self):
        self.env.company.get_chart_of_accounts_or_fail()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Choose how to confirm quotations'),
            'res_model': 'pod_prescriptions.payment.provider.onboarding.wizard',
            'view_mode': 'form',
            'views': [(self.env.ref('payment.payment_provider_onboarding_wizard_form').id, 'form')],
            'target': 'new',
        }
        return action

    @api.model
    def _get_sample_prescriptions_order(self):
        """ Get a sample quotation or create one if it does not exist. """
        # use current user as partner
        partner = self.env.user.partner_id
        company_id = self.env.company.id
        # is there already one?
        sample_prescriptions_order = self.env['prescriptions.order'].search([
            ('company_id', '=', company_id),
            ('partner_id', '=', partner.id),
            ('state', '=', 'draft'),
        ], limit=1)
        if not sample_prescriptions_order:
            # take any existing product or create one
            product = self.env['product.product'].search([], limit=1)
            if not product:
                with file_open('product/static/img/product_product_13-image.jpg', 'rb') as default_image_stream:
                    product = self.env['product.product'].create({
                        'name': _('Sample Product'),
                        'active': False,
                        'image_1920': base64.b64encode(default_image_stream.read()),
                    })
                product.product_tmpl_id.active = False
            sample_prescriptions_order = self.env['prescriptions.order'].create({
                'partner_id': partner.id,
                'order_line': [
                    Command.create({
                        'name': _('Sample Order Line'),
                        'product_id': product.id,
                        'product_uom_qty': 10,
                        'price_unit': 123,
                    })
                ]
            })
        return sample_prescriptions_order

    @api.model
    def action_open_step_sample_quotation(self):
        """ Onboarding step for sending a sample quotation. Open a window to compose an email,
            with the edi_invoice_template message loaded by default. """
        sample_prescriptions_order = self._get_sample_prescriptions_order()
        template = self.env.ref('pod_prescriptions.email_template_edi_prescription', False)

        self.env['mail.compose.message'].with_context(
            mark_rx_as_sent=True,
            default_email_layout_xmlid='mail.mail_notification_layout_with_responsible_signature',
            proforma=self.env.context.get('proforma', False),
        ).create({
            'res_ids': sample_prescriptions_order.ids,
            'template_id': template.id if template else False,
            'model': sample_prescriptions_order._name,
            'composition_mode': 'comment',
        })._action_send_mail()

        self.action_validate_step('pod_prescriptions.onboarding_onboarding_step_sample_quotation')
        prescriptions_quotation_onboarding = self.env.ref('pod_prescriptions.onboarding_onboarding_prescriptions_quotation', raise_if_not_found=False)
        if prescriptions_quotation_onboarding:
            prescriptions_quotation_onboarding.action_close()

        view_id = self.env.ref('pod_prescriptions.view_order_form').id
        action = self.env['ir.actions.actions']._for_xml_id('pod_prescriptions.action_orders')
        action.update({
            'view_mode': 'form',
            'views': [[view_id, 'form']],
            'target': 'main',
        })
        return action

    @api.model
    def action_validate_step_payment_provider(self):
        validation_response = super().action_validate_step_payment_provider()
        if self.env.company.prescriptions_onboarding_payment_method:  # Set if the flow is/was done from the Prescriptions panel
            return self.action_validate_step('pod_prescriptions.onboarding_onboarding_step_prescriptions_order_confirmation')
        return validation_response
