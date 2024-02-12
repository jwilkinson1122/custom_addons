# -*- coding: utf-8 -*-


import binascii

from odoo import fields, exceptions, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request
from odoo.tools import consteq

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager



class CustomerPortal(payment_portal.PaymentPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        Prescription = request.env['prescription']
        if 'quotation_count' in counters:
            values['quotation_count'] = Prescription.search_count(self._prepare_quotations_domain(partner)) \
                if Prescription.check_access_rights('read', raise_exception=False) else 0
        if 'order_count' in counters:
            values['order_count'] = Prescription.search_count(self._prepare_orders_domain(partner), limit=1) \
                if Prescription.check_access_rights('read', raise_exception=False) else 0

        return values

    def _prepare_quotations_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '=', 'sent')
        ]

    def _prepare_orders_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '=', 'prescription'),
        ]

    def _get_prescription_searchbar_sortings(self):
        return {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

    def _prepare_prescription_portal_rendering_values(
        self, page=1, date_begin=None, date_end=None, sortby=None, quotation_page=False, **kwargs
    ):
        Prescription = request.env['prescription']

        if not sortby:
            sortby = 'date'

        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()

        if quotation_page:
            url = "/my/quotes"
            domain = self._prepare_quotations_domain(partner)
        else:
            url = "/my/orders"
            domain = self._prepare_orders_domain(partner)

        searchbar_sortings = self._get_prescription_searchbar_sortings()

        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        pager_values = portal_pager(
            url=url,
            total=Prescription.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        )
        orders = Prescription.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'])

        values.update({
            'date': date_begin,
            'quotations': orders.sudo() if quotation_page else Prescription,
            'orders': orders.sudo() if not quotation_page else Prescription,
            'page_name': 'quote' if quotation_page else 'order',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, **kwargs):
        values = self._prepare_prescription_portal_rendering_values(quotation_page=True, **kwargs)
        request.session['my_quotations_history'] = values['quotations'].ids[:100]
        return request.render("prescription.portal_my_quotations", values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, **kwargs):
        values = self._prepare_prescription_portal_rendering_values(quotation_page=False, **kwargs)
        request.session['my_orders_history'] = values['orders'].ids[:100]
        return request.render("prescription.portal_my_orders", values)

    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(
        self,
        order_id,
        report_type=None,
        access_token=None,
        message=False,
        download=False,
        downpayment=None,
        **kw
    ):
        try:
            order_sudo = self._document_check_access('prescription', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(
                model=order_sudo,
                report_type=report_type,
                report_ref='prescription.action_report_prescription',
                download=download,
            )

        if request.env.user.share and access_token:
            # If a public/portal user accesses the order with the access token
            # Log a note on the chatter.
            today = fields.Date.today().isofoprescriptiont()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if session_obj_date != today:
                # store the date as a string in the session to allow serialization
                request.session['view_quote_%s' % order_sudo.id] = today
                # The "Draft Rx viewed by customer" log note is an infoprescriptiontion
                # dedicated to the personnel and shouldn't be translated in the customer/website lgg
                context = {'lang': order_sudo.user_id.partner_id.lang or order_sudo.company_id.partner_id.lang}
                msg = _('Draft Rx viewed by customer %s', order_sudo.partner_id.name if request.env.user._is_public() else request.env.user.partner_id.name)
                del context
                _message_post_helper(
                    "prescription",
                    order_sudo.id,
                    message=msg,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        backend_url = f'/web#model={order_sudo._name}'\
                      f'&id={order_sudo.id}'\
                      f'&action={order_sudo._get_portal_return_action().id}'\
                      f'&view_type=form'
        values = {
            'prescription': order_sudo,
            'product_documents': order_sudo._get_product_documents(),
            'message': message,
            'report_type': 'html',
            'backend_url': backend_url,
            'res_company': order_sudo.company_id,  # Used to display correct company logo
        }

        # Payment values
        if order_sudo._has_to_be_paid():
            values.update(
                self._get_payment_values(
                    order_sudo,
                    downpayment=downpayment == 'true' if downpayment is not None else order_sudo.prepayment_percent < 1.0
                )
            )

        if order_sudo.state in ('draft', 'sent', 'cancel'):
            history_session_key = 'my_quotations_history'
        else:
            history_session_key = 'my_orders_history'

        values = self._get_page_view_values(
            order_sudo, access_token, values, history_session_key, False)

        return request.render('prescription.prescription_portal_template', values)

    def _get_payment_values(self, order_sudo, downpayment=False, **kwargs):
        """ Return the payment-specific QWeb context values.

        :param prescription order_sudo: The prescription order being paid.
        :param bool downpayment: Whether the current payment is a downpayment.
        :param dict kwargs: Locally unused data passed to `_get_compatible_providers` and
                            `_get_available_tokens`.
        :return: The payment-specific values.
        :rtype: dict
        """
        logged_in = not request.env.user._is_public()
        partner_sudo = request.env.user.partner_id if logged_in else order_sudo.partner_id
        company = order_sudo.company_id
        if downpayment:
            amount = order_sudo._get_prepayment_required_amount()
        else:
            amount = order_sudo.amount_total - order_sudo.amount_paid
        currency = order_sudo.currency_id

        # Select all the payment methods and tokens that match the payment context.
        providers_sudo = request.env['payment.provider'].sudo()._get_compatible_providers(
            company.id,
            partner_sudo.id,
            amount,
            currency_id=currency.id,
            prescription_id=order_sudo.id,
            **kwargs,
        )  # In sudo mode to read the fields of providers and partner (if logged out).
        payment_methods_sudo = request.env['payment.method'].sudo()._get_compatible_payment_methods(
            providers_sudo.ids,
            partner_sudo.id,
            currency_id=currency.id,
        )  # In sudo mode to read the fields of providers.
        tokens_sudo = request.env['payment.token'].sudo()._get_available_tokens(
            providers_sudo.ids, partner_sudo.id, **kwargs
        )  # In sudo mode to read the partner's tokens (if logged out) and provider fields.

        # Make sure that the partner's company matches the invoice's company.
        company_mismatch = not payment_portal.PaymentPortal._can_partner_pay_in_company(
            partner_sudo, company
        )

        portal_page_values = {
            'company_mismatch': company_mismatch,
            'expected_company': company,
        }
        payment_form_values = {
            'show_tokenize_input_mapping': PaymentPortal._compute_show_tokenize_input_mapping(
                providers_sudo, prescription_id=order_sudo.id
            ),
        }
        payment_context = {
            'amount': amount,
            'currency': currency,
            'partner_id': partner_sudo.id,
            'providers_sudo': providers_sudo,
            'payment_methods_sudo': payment_methods_sudo,
            'tokens_sudo': tokens_sudo,
            'transaction_route': order_sudo.get_portal_url(suffix='/transaction'),
            'landing_route': order_sudo.get_portal_url(),
            'access_token': order_sudo._portal_ensure_token(),
        }
        return {
            **portal_page_values,
            **payment_form_values,
            **payment_context,
            **self._get_extra_payment_form_values(**kwargs),
        }

    @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, order_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('prescription', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not order_sudo._has_to_be_signed():
            return {'error': _('The order is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        if not order_sudo._has_to_be_paid():
            order_sudo.action_confirm()
            order_sudo._send_order_confiprescriptiontion_mail()

        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('prescription.action_report_prescription', [order_sudo.id])[0]

        _message_post_helper(
            'prescription',
            order_sudo.id,
            _('Order signed by %s', name),
            attachments=[('%s.pdf' % order_sudo.name, pdf)],
            token=access_token,
        )

        query_string = '&message=sign_ok'
        if order_sudo._has_to_be_paid():
            query_string += '#allow_payment=yes'
        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }

    @http.route(['/my/orders/<int:order_id>/decline'], type='http', auth="public", methods=['POST'], website=True)
    def portal_quote_decline(self, order_id, access_token=None, decline_message=None, **kwargs):
        try:
            order_sudo = self._document_check_access('prescription', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if order_sudo._has_to_be_signed() and decline_message:
            order_sudo._action_cancel()
            _message_post_helper(
                'prescription',
                order_sudo.id,
                decline_message,
                token=access_token,
            )
            redirect_url = order_sudo.get_portal_url()
        else:
            redirect_url = order_sudo.get_portal_url(query_string="&message=cant_reject")

        return request.redirect(redirect_url)

    @http.route('/my/orders/<int:order_id>/document/<int:document_id>', type='http', auth='public')
    def portal_quote_document(self, order_id, document_id, access_token):
        try:
            order_sudo = self._document_check_access('prescription', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        document = request.env['product.document'].browse(document_id).sudo().exists()
        if not document or not document.active:
            return request.redirect('/my')

        if document not in order_sudo._get_product_documents():
            return request.redirect('/my')

        return request.env['ir.binary']._get_stream_from(
            document.ir_attachment_id,
        ).get_response(as_attachment=True)


class PaymentPortal(payment_portal.PaymentPortal):

    @http.route('/my/orders/<int:order_id>/transaction', type='json', auth='public')
    def portal_order_transaction(self, order_id, access_token, **kwargs):
        """ Create a draft transaction and return its processing values.

        :param int order_id: The prescription order to pay, as a `prescription` id
        :param str access_token: The access token used to authenticate the request
        :param dict kwargs: Locally unused data passed to `_create_transaction`
        :return: The mandatory values for the processing of the transaction
        :rtype: dict
        :raise: ValidationError if the invoice id or the access token is invalid
        """
        # Check the order id and the access token
        try:
            order_sudo = self._document_check_access('prescription', order_id, access_token)
        except MissingError as error:
            raise error
        except AccessError:
            raise ValidationError(_("The access token is invalid."))

        logged_in = not request.env.user._is_public()
        partner_sudo = request.env.user.partner_id if logged_in else order_sudo.partner_invoice_id
        self._validate_transaction_kwargs(kwargs)
        kwargs.update({
            'partner_id': partner_sudo.id,
            'currency_id': order_sudo.currency_id.id,
            'prescription_id': order_id,  # Include the SO to allow Subscriptions tokenizing the tx
        })
        tx_sudo = self._create_transaction(
            custom_create_values={'prescription_ids': [Command.set([order_id])]}, **kwargs,
        )

        return tx_sudo._get_processing_values()

    # Payment overrides

    @http.route()
    def payment_pay(self, *args, amount=None, prescription_id=None, access_token=None, **kwargs):
        """ Override of `payment` to replace the missing transaction values by that of the prescription
        order.

        :param str amount: The (possibly partial) amount to pay used to check the access token
        :param str prescription_id: The prescription order for which a payment id made, as a `prescription` id
        :param str access_token: The access token used to authenticate the partner
        :return: The result of the parent method
        :rtype: str
        :raise: ValidationError if the order id is invalid
        """
        # Cast numeric parameters as int or float and void them if their str value is malformed
        amount = self._cast_as_float(amount)
        prescription_id = self._cast_as_int(prescription_id)
        if prescription_id:
            order_sudo = request.env['prescription'].sudo().browse(prescription_id).exists()
            if not order_sudo:
                raise ValidationError(_("The provided parameters are invalid."))

            # Check the access token against the order values. Done after fetching the order as we
            # need the order fields to check the access token.
            if not payment_utils.check_access_token(
                access_token, order_sudo.partner_invoice_id.id, amount, order_sudo.currency_id.id
            ):
                raise ValidationError(_("The provided parameters are invalid."))

            kwargs.update({
                # To display on the payment form; will be later overwritten when creating the tx.
                'reference': order_sudo.name,
                # To fix the currency if incorrect and avoid mismatches when creating the tx.
                'currency_id': order_sudo.currency_id.id,
                # To fix the partner if incorrect and avoid mismatches when creating the tx.
                'partner_id': order_sudo.partner_invoice_id.id,
                'company_id': order_sudo.company_id.id,
                'prescription_id': prescription_id,
            })
        return super().payment_pay(*args, amount=amount, access_token=access_token, **kwargs)

    def _get_extra_payment_form_values(self, prescription_id=None, access_token=None, **kwargs):
        """ Override of `payment` to reroute the payment flow to the portal view of the prescription order.

        :param str prescription_id: The prescription order for which a payment is made, as a `prescription` id.
        :param str access_token: The portal or payment access token, respectively if we are in a
                                 portal or payment link flow.
        :return: The extended rendering context values.
        :rtype: dict
        """
        form_values = super()._get_extra_payment_form_values(
            prescription_id=prescription_id, access_token=access_token, **kwargs
        )
        if prescription_id:
            prescription_id = self._cast_as_int(prescription_id)

            try:  # Check document access against what could be a portal access token.
                order_sudo = self._document_check_access('prescription', prescription_id, access_token)
            except AccessError:  # It is a payment access token computed on the payment context.
                if not payment_utils.check_access_token(
                    access_token,
                    kwargs.get('partner_id'),
                    kwargs.get('amount'),
                    kwargs.get('currency_id'),
                ):
                    raise
                order_sudo = request.env['prescription'].sudo().browse(prescription_id)

            # Interrupt the payment flow if the prescription order has been canceled.
            if order_sudo.state == 'cancel':
                form_values['amount'] = 0.0

            # Reroute the next steps of the payment flow to the portal view of the prescription order.
            form_values.update({
                'transaction_route': order_sudo.get_portal_url(suffix='/transaction'),
                'landing_route': order_sudo.get_portal_url(),
                'access_token': order_sudo.access_token,
            })
        return form_values


class PortalPrescription(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "prescription_count" in counters:
            prescription_model = request.env["prescription"]
            prescription_count = (
                prescription_model.search_count([])
                if prescription_model.check_access_rights("read", raise_exception=False)
                else 0
            )
            values["prescription_count"] = prescription_count
        return values

    def _prescription_get_page_view_values(self, prescription, access_token, **kwargs):
        values = {
            "page_name": "Prescriptions",
            "prescription": prescription,
        }
        return self._get_page_view_values(
            prescription, access_token, values, "my_prescriptions_history", False, **kwargs
        )

    def _get_filter_domain(self, kw):
        return []

    @http.route(
        ["/my/prescriptions", "/my/prescriptions/page/<int:page>"], type="http", auth="user", website=True
    )
    def portal_my_prescriptions(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        prescription_obj = request.env["prescription"]
        # Avoid error if the user does not have access.
        if not prescription_obj.check_access_rights("read", raise_exception=False):
            return request.redirect("/my")
        domain = self._get_filter_domain(kw)
        searchbar_sortings = {
            "date": {"label": _("Date"), "order": "date desc"},
            "name": {"label": _("Name"), "order": "name desc"},
            "state": {"label": _("Status"), "order": "state"},
        }
        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]
        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]
        # count for pager
        prescription_count = prescription_obj.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/prescriptions",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
            },
            total=prescription_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        prescriptions = prescription_obj.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_prescriptions_history"] = prescriptions.ids[:100]
        values.update(
            {
                "date": date_begin,
                "prescriptions": prescriptions,
                "page_name": "Prescriptions",
                "pager": pager,
                "default_url": "/my/prescriptions",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("prescription.portal_my_prescriptions", values)

    @http.route(["/my/prescriptions/<int:prescription_id>"], type="http", auth="public", website=True)
    def portal_my_prescription_detail(
        self, prescription_id, access_token=None, report_type=None, download=False, **kw
    ):
        try:
            prescription_sudo = self._document_check_access("prescription", prescription_id, access_token)
        except (AccessError, MissingError):
            return request.redirect("/my")
        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=prescription_sudo,
                report_type=report_type,
                report_ref="prescription.report_prescription_action",
                download=download,
            )

        values = self._prescription_get_page_view_values(prescription_sudo, access_token, **kw)
        return request.render("prescription.portal_prescription_page", values)

    @http.route(
        ["/my/prescriptions/picking/pdf/<int:prescription_id>/<int:picking_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_prescription_picking_report(self, prescription_id, picking_id, access_token=None, **kw):
        try:
            picking_sudo = self._picking_check_access(
                prescription_id, picking_id, access_token=access_token
            )
        except exceptions.AccessError:
            return request.redirect("/my")
        report_sudo = request.env.ref("stock.action_report_delivery").sudo()
        pdf = report_sudo._render_qweb_pdf([picking_sudo.id])[0]
        pdfhttpheaders = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    def _picking_check_access(self, prescription_id, picking_id, access_token=None):
        prescription = request.env["prescription"].browse([prescription_id])
        picking = request.env["stock.picking"].browse([picking_id])
        picking_sudo = picking.sudo()
        try:
            picking.check_access_rights("read")
            picking.check_access_rule("read")
        except exceptions.AccessError:
            if not access_token or not consteq(prescription.access_token, access_token):
                raise
        return picking_sudo
