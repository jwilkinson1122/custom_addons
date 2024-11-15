# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import http, _
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.addons.portal.controllers.portal import CustomerPortal
import re
from odoo.http import request, content_disposition


class DownloadReport(http.Controller):

    def _document_check_access(self, model_name, document_id, access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.sudo().exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        if access_token and document_sudo.report_token and access_token == document_sudo.report_token:
            return document_sudo
        else:
            raise AccessError(
                "Sorry, you are not allowed to access this document.")

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))

        report_sudo = request.env.ref(report_ref).sudo()

        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(
                _("%s is not the reference of a report", report_ref))

        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)(
            [model.id], data={'report_type': report_type})[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (
                re.sub('\W+', '-', model._get_report_base_filename()))
            reporthttpheaders.append(
                ('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)

    @http.route(['/download/diagnosis/<int:diagnosis_id>'], type='http', auth="public", website=True)
    def download_order(self, diagnosis_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access(
                'sh.patho.request', diagnosis_id, access_token=access_token)
        except (AccessError, MissingError):
            return '<br/><br/><center><h1><b>Oops Invalid URL! Please check URL and try again!</b></h1></center>'
        report_type = 'pdf'
        download = True
        return self._show_report(model=order_sudo, report_type=report_type, report_ref='sh_pathology_management.action_report_patient', download=download)


class ShCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        diagnosis_entry = request.env['sh.patho.request.line'].sudo()

        if 'diagnosis_count' in counters:
            values['diagnosis_count'] = diagnosis_entry.search_count([
                ('patient_details_id', '=', request.env.user.sudo().partner_id.id)
            ])if diagnosis_entry.check_access_rights('read', raise_exception=False) else 0
        return values

    @http.route(['/my/diagnosis', '/my/diagnosis/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes1(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        DiagnosisEntry = request.env['sh.patho.request.line'].sudo()

        domain = [('patient_details_id', '=',
                   request.env.user.sudo().partner_id.id)]
        entry = DiagnosisEntry.search(domain)

        values.update({
            'entry': entry.sudo(),
            'default_url': '/my/diagnosis',
            'page_name': 'diagnosis',

        })
        return request.render("sh_pathology_management.portal_my_diagnosis", values)

    @http.route(['/my/diagnosis/<int:line_id>'], type='http', auth="public", website=True)
    def portal_entry_page1(self, line_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access(
                'sh.patho.request.line', line_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo.patho_request_id, report_type=report_type, report_ref='sh_pathology_management.action_report_patient', download=download)

        values = {
            'sh_patho_request_line': order_sudo,
            'message': message,
            'token': access_token,
            # 'return_url': '/my/entry',
            'bootstrap_formatting': True,
            # 'report_type': 'html',
            'action': order_sudo.get_portal_url(),
        }
        return request.render('sh_pathology_management.diagnosis_entry_portal_template', values)
