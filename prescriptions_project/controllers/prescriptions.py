# -*- coding: utf-8 -*-


import logging

from odoo import http
from odoo.addons.prescriptions.controllers.prescriptions import ShareRoute
from odoo.http import request

logger = logging.getLogger(__name__)


class ProjectShareRoute(ShareRoute):

    def _create_uploaded_prescriptions(self, files, share, folder, prescriptions_values=None):
        prescriptions_values = prescriptions_values or {}
        project = folder._get_project_from_closest_ancestor()
        if project:
            prescriptions_values.update({
                'res_model': 'project.project',
                'res_id': project.id,
                'tag_ids': project.prescriptions_tag_ids.ids,
            })
            if project.partner_id and not share.partner_id.id:
                prescriptions_values['partner_id'] = project.partner_id.id
        return super()._create_uploaded_prescriptions(files, share, folder, prescriptions_values)

    @http.route()
    def upload_prescription(self, folder_id, ufile, tag_ids, **kwargs):
        if not kwargs.get('res_model') and not kwargs.get('res_id'):
            current_folder = request.env['prescriptions.folder'].browse(int(folder_id))
            project = current_folder._get_project_from_closest_ancestor()
            if project:
                kwargs.update({
                    'res_model': 'project.project',
                    'res_id': project.id,
                })
                if project.partner_id:
                    kwargs['partner_id'] = project.partner_id.id
                if not tag_ids:
                    tag_ids = ','.join(str(tag_id) for tag_id in project.prescriptions_tag_ids.ids)
        return super().upload_prescription(folder_id, ufile, tag_ids, **kwargs)
