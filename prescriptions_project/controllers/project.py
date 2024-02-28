# -*- coding: utf-8 -*-


import base64
import logging

from odoo import http
from odoo.addons.prescriptions.controllers.prescriptions import ShareRoute
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

logger = logging.getLogger(__name__)


class PrescriptionsProjectShareRoute(http.Controller):

# ------------------------------------------------------------------------------
# Business methods
# ------------------------------------------------------------------------------

    def _check_access_and_get_task_from_project(self, project_id, task_id, access_token):
        CustomerPortal._prescription_check_access(self, 'project.project', project_id, access_token)
        return request.env['project.task'].sudo().search([('project_id', '=', project_id), ('id', '=', task_id)], limit=1)

    def _check_access_and_get_shared_prescriptions(self, project_id=None, task_id=None, prescription_ids=None, access_token=None):
        if task_id and project_id:
            record_sudo = self._check_access_and_get_task_from_project(project_id, task_id, access_token)
        else:
            record_sudo = CustomerPortal._prescription_check_access(self, 'project.project' if project_id else 'project.task', project_id or task_id, access_token)

        prescriptions = record_sudo.shared_prescription_ids
        if prescription_ids:
            prescriptions = prescriptions.filtered(lambda prescription: prescription.id in prescription_ids)
        if not prescriptions:
            raise request.not_found()
        return prescriptions

    def _get_prescription_owner_avatar(self, prescription):
        user_id = prescription.owner_id.id
        avatar = request.env['res.users'].sudo().browse(user_id).avatar_128

        if not avatar:
            return request.env['ir.http']._placeholder()
        return base64.b64decode(avatar)

# ------------------------------------------------------------------------------
# Project routes
# ------------------------------------------------------------------------------

    @http.route('/my/projects/<int:project_id>/prescriptions', type='http', auth='public')
    def portal_my_project_prescriptions(self, project_id, access_token=None, **kwargs):
        try:
            project_sudo = CustomerPortal._prescription_check_access(self, 'project.project', project_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        available_prescriptions = project_sudo.shared_prescription_ids
        if not available_prescriptions:
            return request.not_found()

        options = {
            'base_url': f"/my/projects/{project_id}/prescriptions/",
            'upload': project_sudo.prescriptions_folder_id.is_shared,
            'prescription_ids': available_prescriptions,
            'all_button': len(available_prescriptions) > 1 and 'binary' in available_prescriptions.mapped('type'),
            'access_token': access_token,
        }
        return request.render('prescriptions_project.share_page', options)

    @http.route('/my/projects/<int:project_id>/prescriptions/<int:prescription_id>/thumbnail', type='http', auth='public')
    def portal_my_project_prescription_thumbnail(self, project_id, prescription_id, access_token=None, **kwargs):
        try:
            prescription = self._check_access_and_get_shared_prescriptions(project_id, prescription_ids=[prescription_id], access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        try:
            return request.env['ir.binary']._get_stream_from(prescription, 'thumbnail').get_response()
        except Exception:
            return request.not_found()

    @http.route('/my/projects/<int:project_id>/prescriptions/<int:prescription_id>/avatar', type='http', auth='public')
    def portal_my_project_prescription_avatar(self, project_id, prescription_id, access_token=None, **kwargs):
        try:
            prescription = self._check_access_and_get_shared_prescriptions(project_id, prescription_ids=[prescription_id], access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        return self._get_prescription_owner_avatar(prescription)

    @http.route('/my/projects/<int:project_id>/prescriptions/<int:prescription_id>/download', type='http', auth='public')
    def portal_my_project_prescriptions_download(self, project_id, prescription_id, access_token=None, preview=None, **kwargs):
        try:
            prescription = self._check_access_and_get_shared_prescriptions(project_id, prescription_ids=[prescription_id], access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.env['ir.binary']._get_stream_from(prescription).get_response(as_attachment=not bool(preview))

    @http.route('/my/projects/<int:project_id>/prescriptions/download', type='http', auth='public')
    def portal_my_project_prescriptions_download_all(self, project_id, access_token=None, **kwargs):
        try:
            prescriptions = self._check_access_and_get_shared_prescriptions(project_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if not prescriptions:
            raise request.not_found()

        project_name = request.env['project.project'].browse(project_id).name
        return ShareRoute._make_zip(project_name + '.zip', prescriptions)

    @http.route('/my/projects/<int:project_id>/prescriptions/upload', type='http', auth='public', methods=['POST'], csrf=False)
    def portal_my_project_prescription_upload(self, project_id, access_token=None, **kwargs):
        try:
            project_sudo = CustomerPortal._prescription_check_access(self, 'project.project', project_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        folder = project_sudo.prescriptions_folder_id

        try:
            prescriptions_vals = []
            for file in request.httprequest.files.getlist('files'):
                data = file.read()
                prescription_vals = {
                    'mimetype': file.content_type,
                    'name': file.filename,
                    'datas': base64.b64encode(data),
                    'partner_id': project_sudo.partner_id.id,
                    'owner_id': request.env.user.id,
                    'folder_id': folder.id,
                    'tag_ids': project_sudo.prescriptions_tag_ids.ids,
                    'res_model': 'project.project',
                    'res_id': project_sudo.id,
                }
                prescriptions_vals.append(prescription_vals)
            request.env['prescriptions.prescription'].sudo().create(prescriptions_vals)

        except Exception:
            logger.exception("Failed to upload prescription")

        token_string = f"access_token={access_token}" if access_token else ""
        return request.redirect(f"/my/projects/{project_id}/prescriptions?" + token_string)

# ------------------------------------------------------------------------------
# Task routes
# ------------------------------------------------------------------------------

    @http.route([
        '/my/tasks/<int:task_id>/prescriptions',
        '/my/projects/<int:project_id>/task/<int:task_id>/prescriptions',
    ], type='http', auth='public')
    def portal_my_task_prescriptions(self, task_id, project_id=None, access_token=None, **kwargs):
        try:
            if project_id:
                task_sudo = self._check_access_and_get_task_from_project(project_id, task_id, access_token)
            else:
                task_sudo = CustomerPortal._prescription_check_access(self, 'project.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        available_prescriptions = task_sudo.shared_prescription_ids
        if not available_prescriptions:
            return request.not_found()

        options = {
            'base_url': f"/my/projects/{project_id}/task/{task_id}/prescriptions/" if project_id else f"/my/tasks/{task_id}/prescriptions/",
            'upload': task_sudo.prescriptions_folder_id.is_shared,
            'prescription_ids': available_prescriptions,
            'all_button': len(available_prescriptions) > 1 and 'binary' in available_prescriptions.mapped('type'),
            'access_token': access_token,
        }
        return request.render('prescriptions_project.share_page', options)

    @http.route([
        '/my/tasks/<int:task_id>/prescriptions/<int:prescription_id>/thumbnail',
        '/my/projects/<int:project_id>/task/<int:task_id>/prescriptions/<int:prescription_id>/thumbnail',
    ], type='http', auth='public')
    def portal_my_task_prescription_thumbnail(self, task_id, prescription_id, project_id=None, access_token=None, **kwargs):
        try:
            prescription = self._check_access_and_get_shared_prescriptions(project_id, task_id, [prescription_id], access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        try:
            return request.env['ir.binary']._get_stream_from(prescription, 'thumbnail').get_response()
        except Exception:
            return request.not_found()

    @http.route([
        '/my/tasks/<int:task_id>/prescriptions/<int:prescription_id>/avatar',
        '/my/projects/<int:project_id>/task/<int:task_id>/prescriptions/<int:prescription_id>/avatar',
    ], type='http', auth='public')
    def portal_my_task_prescription_avatar(self, task_id, prescription_id, project_id=None, access_token=None, **kwargs):
        try:
            prescription = self._check_access_and_get_shared_prescriptions(project_id, task_id, [prescription_id], access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        return self._get_prescription_owner_avatar(prescription)

    @http.route([
        '/my/tasks/<int:task_id>/prescriptions/<int:prescription_id>/download',
        '/my/projects/<int:project_id>/task/<int:task_id>/prescriptions/<int:prescription_id>/download',
    ], type='http', auth='public')
    def portal_my_task_prescriptions_download(self, task_id, prescription_id, project_id=None, access_token=None, preview=None, **kwargs):
        try:
            prescription = self._check_access_and_get_shared_prescriptions(project_id, task_id, [prescription_id], access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.env['ir.binary']._get_stream_from(prescription).get_response(as_attachment=not bool(preview))

    @http.route([
        '/my/tasks/<int:task_id>/prescriptions/download',
        '/my/projects/<int:project_id>/task/<int:task_id>/prescriptions/download',
    ], type='http', auth='public')
    def portal_my_task_prescriptions_download_all(self, task_id, project_id=None, access_token=None, **kwargs):
        try:
            prescriptions = self._check_access_and_get_shared_prescriptions(project_id, task_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if not prescriptions:
            raise request.not_found()

        task_name = request.env['project.task'].sudo().browse(task_id).name
        return ShareRoute._make_zip(task_name + '.zip', prescriptions)

    @http.route([
        '/my/tasks/<int:task_id>/prescriptions/upload',
        '/my/projects/<int:project_id>/task/<int:task_id>/prescriptions/upload',
    ], type='http', auth='public', methods=['POST'], csrf=False)
    def portal_my_task_prescription_upload(self, task_id, project_id=None, access_token=None, **kwargs):
        try:
            if project_id:
                task_sudo = self._check_access_and_get_task_from_project(project_id, task_id, access_token)
            else:
                task_sudo = CustomerPortal._prescription_check_access(self, 'project.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        folder = task_sudo.project_id.prescriptions_folder_id

        try:
            prescriptions_vals = []
            for file in request.httprequest.files.getlist('files'):
                data = file.read()
                prescription_vals = {
                    'mimetype': file.content_type,
                    'name': file.filename,
                    'datas': base64.b64encode(data),
                    'partner_id': task_sudo.partner_id.id,
                    'owner_id': request.env.user.id,
                    'folder_id': folder.id,
                    'tag_ids': task_sudo.project_id.prescriptions_tag_ids.ids,
                    'res_model': 'project.task',
                    'res_id': task_sudo.id,
                }
                prescriptions_vals.append(prescription_vals)
            request.env['prescriptions.prescription'].sudo().create(prescriptions_vals)

        except Exception:
            logger.exception("Failed to upload prescription")

        token_string = f"access_token={access_token}" if access_token else ""
        return request.redirect((f"/my/projects/{project_id}/task/{task_id}/prescriptions/" if project_id else f"/my/tasks/{task_id}/prescriptions/") + f"?{token_string}")
