

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    # Defaults
    default_invoice_policy = fields.Selection(
        selection=[
            ('order', "Invoice what is ordered"),
            ('delivery', "Invoice what is delivered")
        ],
        string="Invoicing Policy",
        default='order',
        default_model='product.template')

    # Groups
    group_product_variant = fields.Boolean("Variants", implied_group='product.group_product_variant')

    group_auto_done_setting = fields.Boolean(
        string="Lock Confirmed Prescription", implied_group='prescription.group_auto_done_setting')
    # group_proforma_prescription = fields.Boolean(
    #     string="Pro-Forma Invoice", implied_group='prescription.group_proforma_prescription',
    #     help="Allows you to send pro-forma invoice.")
    group_warning_prescription = fields.Boolean(
        string="Prescription Order Warnings", implied_group='prescription.group_warning_prescription')

    # Config params
    automatic_invoice = fields.Boolean(
        string="Automatic Invoice",
        help="The invoice is generated automatically and available in the customer portal when the "
             "transaction is confirmed by the payment provider.\nThe invoice is marked as paid and "
             "the payment is registered in the payment journal defined in the configuration of the "
             "payment provider.\nThis mode is advised if you issue the final invoice at the order "
             "and not after the delivery.",
        config_parameter='prescription.automatic_invoice',
    )
    deposit_default_product_id = fields.Many2one(
        related='company_id.prescription_down_payment_product_id',
        readonly=False,
        # previously config_parameter='prescription.default_deposit_product_id',
    )

    invoice_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        string="Invoice Email Template",
        domain=[('model', '=', 'account.move')],
        config_parameter='prescription.default_invoice_email_template',
        help="Email sent to the customer once the invoice is available.",
    )
    quotation_validity_days = fields.Integer(
        related='company_id.quotation_validity_days',
        readonly=False)
    portal_confirmation_sign = fields.Boolean(
        related='company_id.portal_confirmation_sign',
        readonly=False)
    portal_confirmation_pay = fields.Boolean(
        related='company_id.portal_confirmation_pay',
        readonly=False)
    prepayment_percent = fields.Float(
        related='company_id.prepayment_percent',
        readonly=False)

    # Modules
    module_prescription_product_matrix = fields.Boolean("Prescription Grid Entry")
    
    module_delivery = fields.Boolean("Delivery Methods")
    module_delivery_bpost = fields.Boolean("bpost Connector")
    module_delivery_dhl = fields.Boolean("DHL Express Connector")
    module_delivery_easypost = fields.Boolean("Easypost Connector")
    module_delivery_fedex = fields.Boolean("FedEx Connector")
    module_delivery_sendcloud = fields.Boolean("Sendcloud Connector")
    module_delivery_shiprocket = fields.Boolean("Shiprocket Connector")
    module_delivery_ups = fields.Boolean("UPS Connector")
    module_delivery_usps = fields.Boolean("USPS Connector")

    module_product_email_template = fields.Boolean("Specific Email")
    module_prescription_amazon = fields.Boolean("Amazon Sync")
    module_prescription_loyalty = fields.Boolean("Coupons & Loyalty")
    module_prescription_margin = fields.Boolean("Margins")
    module_prescription_pdf_quote_builder = fields.Boolean("PDF Quote builder")

    #=== ONCHANGE METHODS ===#
    
    @api.onchange('group_product_variant')
    def _onchange_group_product_variant(self):
        """The product Configurator requires the product variants activated.
        If the user disables the product variants -> disable the product configurator as well"""
        if self.module_prescription_product_matrix and not self.group_product_variant:
            self.module_prescription_product_matrix = False

    @api.onchange('portal_confirmation_pay')
    def _onchange_portal_confirmation_pay(self):
        self.prepayment_percent = self.prepayment_percent or 1.0

    @api.onchange('prepayment_percent')
    def _onchange_prepayment_percent(self):
        if not self.prepayment_percent:
            self.portal_confirmation_pay = False

    @api.onchange('quotation_validity_days')
    def _onchange_quotation_validity_days(self):
        if self.quotation_validity_days < 0:
            self.quotation_validity_days = self.env['res.company'].default_get(
                ['quotation_validity_days']
            )['quotation_validity_days']
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("Draft Rx Validity is required and must be greater or equal to 0."),
                },
            }

    #=== CRUD METHODS ===#

    def set_values(self):
        super().set_values()
        if self.default_invoice_policy != 'order':
            self.env['ir.config_parameter'].set_param('prescription.automatic_invoice', False)

        send_invoice_cron = self.env.ref('prescription.send_invoice_cron', raise_if_not_found=False)
        if send_invoice_cron and send_invoice_cron.active != self.automatic_invoice:
            send_invoice_cron.active = self.automatic_invoice
