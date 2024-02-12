

from datetime import datetime
from dateutil import relativedelta

from odoo import _, api, Command, fields, models, SUPERUSER_ID
from odoo.tools import str2bool


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    prescription_ids = fields.Many2many('prescription', 'prescription_transaction_rel', 'transaction_id', 'prescription_id',
                                      string='Prescription Orders', copy=False, readonly=True)
    prescription_ids_nbr = fields.Integer(compute='_compute_prescription_ids_nbr', string='# of Prescription Orders')

    def _compute_prescription_reference(self, order):
        self.ensure_one()
        if self.provider_id.so_reference_type == 'so_name':
            order_reference = order.name
        else:
            # self.provider_id.so_reference_type == 'partner'
            identification_number = order.partner_id.id
            order_reference = '%s/%s' % ('CUST', str(identification_number % 97).rjust(2, '0'))

        invoice_journal = self.env['account.journal'].search([('type', '=', 'prescription'), ('company_id', '=', self.env.company.id)], limit=1)
        if invoice_journal:
            order_reference = invoice_journal._process_reference_for_prescription(order_reference)

        return order_reference

    @api.depends('prescription_ids')
    def _compute_prescription_ids_nbr(self):
        for trans in self:
            trans.prescription_ids_nbr = len(trans.prescription_ids)

    def _set_pending(self, state_message=None, **kwargs):
        """ Override of `payment` to send the quotations automatically.

        :param str state_message: The reason for which the transaction is set in 'pending' state.
        :return: updated transactions.
        :rtype: `payment.transaction` recordset.
        """
        txs_to_process = super()._set_pending(state_message=state_message, **kwargs)

        for tx in txs_to_process:  # Consider only transactions that are indeed set pending.
            prescriptions = tx.prescription_ids.filtered(lambda so: so.state in ['draft', 'sent'])
            prescriptions.filtered(
                lambda so: so.state == 'draft'
            ).with_context(tracking_disable=True).action_quotation_sent()

            if tx.provider_id.code == 'custom':
                for so in tx.prescription_ids:
                    so.reference = tx._compute_prescription_reference(so)
            # send payment status mail.
            prescriptions._send_payment_succeeded_for_order_mail()

        return txs_to_process

    def _check_amount_and_confirm_order(self):
        """ Confirm the prescription order based on the amount of a transaction.

        Confirm the prescription orders only if the transaction amount (or the sum of the partial
        transaction amounts) is equal to or greater than the required amount for order confirmation

        Grouped payments (paying multiple prescription orders in one transaction) are not supported.

        :return: The confirmed prescription orders.
        :rtype: a `prescription` recordset
        """
        confirmed_orders = self.env['prescription']
        for tx in self:
            # We only support the flow where exactly one quotation is linked to a transaction.
            if len(tx.prescription_ids) == 1:
                quotation = tx.prescription_ids.filtered(lambda so: so.state in ('draft', 'sent'))
                if quotation and quotation._is_confirmation_amount_reached():
                    quotation.with_context(send_email=True).action_confirm()
                    confirmed_orders |= quotation
        return confirmed_orders

    def _set_authorized(self, state_message=None, **kwargs):
        """ Override of payment to confirm the quotations automatically. """
        super()._set_authorized(state_message=state_message, **kwargs)
        confirmed_orders = self._check_amount_and_confirm_order()
        confirmed_orders._send_order_confirmation_mail()
        (self.prescription_ids - confirmed_orders)._send_payment_succeeded_for_order_mail()

    def _log_message_on_linked_documents(self, message):
        """ Override of payment to log a message on the prescription orders linked to the transaction.

        Note: self.ensure_one()

        :param str message: The message to be logged
        :return: None
        """
        super()._log_message_on_linked_documents(message)
        self = self.with_user(SUPERUSER_ID)  # Log messages as 'OdooBot'
        for order in self.prescription_ids or self.source_transaction_id.prescription_ids:
            order.message_post(body=message)

    def _reconcile_after_done(self):
        """ Override of payment to automatically confirm quotations and generate invoices. """
        confirmed_orders = self._check_amount_and_confirm_order()
        confirmed_orders._send_order_confirmation_mail()
        (self.prescription_ids - confirmed_orders)._send_payment_succeeded_for_order_mail()

        auto_invoice = str2bool(
            self.env['ir.config_parameter'].sudo().get_param('prescription.automatic_invoice'))
        if auto_invoice:
            # Invoice the prescription orders in self instead of in confirmed_orders to create the invoice
            # even if only a partial payment was made.
            self._invoice_prescriptions()
        super()._reconcile_after_done()
        if auto_invoice:
            # Must be called after the super() call to make sure the invoice are correctly posted.
            self._send_invoice()

    def _send_invoice(self):
        template_id = int(self.env['ir.config_parameter'].sudo().get_param(
            'prescription.default_invoice_email_template',
            default=0
        ))
        if not template_id:
            return
        template = self.env['mail.template'].browse(template_id).exists()
        if not template:
            return

        for tx in self:
            tx = tx.with_company(tx.company_id).with_context(
                company_id=tx.company_id.id,
            )
            invoice_to_send = tx.invoice_ids.filtered(
                lambda i: not i.is_move_sent and i.state == 'posted' and i._is_ready_to_be_sent()
            )
            invoice_to_send.is_move_sent = True # Mark invoice as sent
            invoice_to_send.with_user(SUPERUSER_ID)._generate_pdf_and_send_invoice(template)

    def _cron_send_invoice(self):
        """
            Cron to send invoice that where not ready to be send directly after posting
        """
        if not self.env['ir.config_parameter'].sudo().get_param('prescription.automatic_invoice'):
            return

        # No need to retrieve old transactions
        retry_limit_date = datetime.now() - relativedelta.relativedelta(days=2)
        # Retrieve all transactions matching the criteria for post-processing
        self.search([
            ('state', '=', 'done'),
            ('is_post_processed', '=', True),
            ('invoice_ids', 'in', self.env['account.move']._search([
                ('is_move_sent', '=', False),
                ('state', '=', 'posted'),
            ])),
            ('prescription_ids.state', '=', 'prescription'),
            ('last_state_change', '>=', retry_limit_date),
        ])._send_invoice()

    def _invoice_prescriptions(self):
        for tx in self.filtered(lambda tx: tx.prescription_ids):
            tx = tx.with_company(tx.company_id)

            confirmed_orders = tx.prescription_ids.filtered(lambda so: so.state == 'prescription')
            if confirmed_orders:
                # Filter orders between those fully paid and those partially paid.
                fully_paid_orders = confirmed_orders.filtered(lambda so: so._is_paid())

                # Create a down payment invoice for partially paid orders
                downpayment_invoices = (
                    confirmed_orders - fully_paid_orders
                )._generate_downpayment_invoices()

                # For fully paid orders create a final invoice.
                fully_paid_orders._force_lines_to_invoice_policy_order()
                final_invoices = fully_paid_orders.with_context(
                    raise_if_nothing_to_invoice=False
                )._create_invoices(final=True)
                invoices = downpayment_invoices + final_invoices

                # Setup access token in advance to avoid serialization failure between
                # edi postprocessing of invoice and displaying the prescription order on the portal
                for invoice in invoices:
                    invoice._portal_ensure_token()
                tx.invoice_ids = [Command.set(invoices.ids)]

    @api.model
    def _compute_reference_prefix(self, provider_code, separator, **values):
        """ Override of payment to compute the reference prefix based on Prescription-specific values.

        If the `values` parameter has an entry with 'prescription_ids' as key and a list of (4, id, O)
        or (6, 0, ids) X2M command as value, the prefix is computed based on the prescription order name(s)
        Otherwise, the computation is delegated to the super method.

        :param str provider_code: The code of the provider handling the transaction
        :param str separator: The custom separator used to separate data references
        :param dict values: The transaction values used to compute the reference prefix. It should
                            have the structure {'prescription_ids': [(X2M command), ...], ...}.
        :return: The computed reference prefix if order ids are found, the one of `super` otherwise
        :rtype: str
        """
        command_list = values.get('prescription_ids')
        if command_list:
            # Extract prescription order id(s) from the X2M commands
            order_ids = self._fields['prescription_ids'].convert_to_cache(command_list, self)
            orders = self.env['prescription'].browse(order_ids).exists()
            if len(orders) == len(order_ids):  # All ids are valid
                return separator.join(orders.mapped('name'))
        return super()._compute_reference_prefix(provider_code, separator, **values)

    def action_view_prescriptions(self):
        action = {
            'name': _('Prescription Order(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'prescription',
            'target': 'current',
        }
        prescription_ids = self.prescription_ids.ids
        if len(prescription_ids) == 1:
            action['res_id'] = prescription_ids[0]
            action['view_mode'] = 'form'
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', prescription_ids)]
        return action
