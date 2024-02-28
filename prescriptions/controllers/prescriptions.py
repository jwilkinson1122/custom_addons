# -*- coding: utf-8 -*-

import base64
import io
import json
import logging
import zipfile
from contextlib import ExitStack

from markupsafe import Markup
from werkzeug.exceptions import Forbidden

from odoo import Command, http
from odoo.exceptions import AccessError
from odoo.http import request, content_disposition
from odoo.tools.translate import _

logger = logging.getLogger(__name__)


class ShareRoute(http.Controller):

    # util methods #################################################################################

    def _get_file_response(self, res_id, share_id=None, share_token=None, field='raw', as_attachment=None):
        """ returns the http response to download one file. """
        record = request.env['prescriptions.prescription'].browse(int(res_id))

        if share_id:
            share = request.env['prescriptions.share'].sudo().browse(int(share_id))
            record = share._get_prescriptions_and_check_access(share_token, [int(res_id)], operation='read')
        if not record or not record.exists():
            raise request.not_found()

        if record.type == 'url':
            if isinstance(record.url, str):
                url = record.url if record.url.startswith(('http://', 'https://', 'ftp://')) else 'http://' + record.url
            else:
                url = record.url
            return request.redirect(url, code=307, local=False)

        filename = (record.name if not record.file_extension or record.name.endswith(f'.{record.file_extension}')
                    else f'{record.name}.{record.file_extension}')
        return request.env['ir.binary']._get_stream_from(record, field, filename=filename).get_response(as_attachment)

    @classmethod
    def _get_downloadable_prescriptions(cls, prescriptions):
        """Only files are downloadable."""
        return prescriptions.filtered(lambda d: d.type == "binary")

    @classmethod
    def _make_zip(cls, name, prescriptions):
        streams = (
            request.env['ir.binary']._get_stream_from(prescription, 'raw')
            for prescription in cls._get_downloadable_prescriptions(prescriptions)
        )
        return cls._generate_zip(name, streams)

    @classmethod
    def _generate_zip(cls, name, file_streams):
        """returns zip files for the Prescription Inspector and the portal.

        :param name: the name to give to the zip file.
        :param file_streams: binary file streams to be zipped.
        :return: a http response to download a zip file.
        """
        # TODO: zip on-the-fly while streaming instead of loading the
        #       entire zip in memory and sending it all at once.

        stream = io.BytesIO()
        try:
            with zipfile.ZipFile(stream, 'w') as doc_zip:
                for binary_stream in file_streams:
                    if not binary_stream:
                        continue
                    doc_zip.writestr(
                        binary_stream.download_name,
                        binary_stream.read(),  # Cf Todo: this is bad
                        compress_type=zipfile.ZIP_DEFLATED
                    )
        except zipfile.BadZipfile:
            logger.exception("BadZipfile exception")

        content = stream.getvalue()  # Cf Todo: this is bad
        headers = [
            ('Content-Type', 'zip'),
            ('X-Content-Type-Options', 'nosniff'),
            ('Content-Length', len(content)),
            ('Content-Disposition', content_disposition(name))
        ]
        return request.make_response(content, headers)

    # Download & upload routes #####################################################################

    @http.route('/prescriptions/upload_attachment', type='http', methods=['POST'], auth="user")
    def upload_prescription(self, folder_id, ufile, tag_ids, prescription_id=False, partner_id=False, owner_id=False, res_id=False, res_model=False):
        files = request.httprequest.files.getlist('ufile')
        result = {'success': _("All files uploaded")}
        tag_ids = tag_ids.split(',') if tag_ids else []
        if prescription_id:
            prescription = request.env['prescriptions.prescription'].browse(int(prescription_id))
            ufile = files[0]
            try:
                data = base64.encodebytes(ufile.read())
                mimetype = ufile.content_type
                prescription.write({
                    'name': ufile.filename,
                    'datas': data,
                    'mimetype': mimetype,
                })
            except Exception as e:
                logger.exception("Fail to upload prescription %s" % ufile.filename)
                result = {'error': str(e)}
        else:
            vals_list = []
            for ufile in files:
                try:
                    mimetype = ufile.content_type
                    datas = base64.encodebytes(ufile.read())
                    vals = {
                        'name': ufile.filename,
                        'mimetype': mimetype,
                        'datas': datas,
                        'folder_id': int(folder_id),
                        'tag_ids': tag_ids,
                        'partner_id': int(partner_id)
                    }
                    if owner_id:
                        vals['owner_id'] = int(owner_id)
                    if res_id and res_model:
                        vals['res_id'] = res_id
                        vals['res_model'] = res_model
                    vals_list.append(vals)
                except Exception as e:
                    logger.exception("Fail to upload prescription %s" % ufile.filename)
                    result = {'error': str(e)}
            cids = request.httprequest.cookies.get('cids', str(request.env.user.company_id.id))
            allowed_company_ids = [int(cid) for cid in cids.split(',')]
            prescriptions = request.env['prescriptions.prescription'].with_context(allowed_company_ids=allowed_company_ids).create(vals_list)
            result['ids'] = prescriptions.ids

        return json.dumps(result)

    @http.route('/prescriptions/pdf_split', type='http', methods=['POST'], auth="user")
    def pdf_split(self, new_files=None, ufile=None, archive=False, vals=None):
        """Used to split and/or merge pdf prescriptions.

        The data can come from different sources: multiple existing prescriptions
        (at least one must be provided) and any number of extra uploaded files.

        :param new_files: the array that represents the new pdf structure:
            [{
                'name': 'New File Name',
                'new_pages': [{
                    'old_file_type': 'prescription' or 'file',
                    'old_file_index': prescription_id or index in ufile,
                    'old_page_number': 5,
                }],
            }]
        :param ufile: extra uploaded files that are not existing prescriptions
        :param archive: whether to archive the original prescriptions
        :param vals: values for the create of the new prescriptions.
        """
        vals = json.loads(vals)
        new_files = json.loads(new_files)
        # find original prescriptions
        prescription_ids = set()
        for new_file in new_files:
            for page in new_file['new_pages']:
                if page['old_file_type'] == 'prescription':
                    prescription_ids.add(page['old_file_index'])
        prescriptions = request.env['prescriptions.prescription'].browse(prescription_ids)

        with ExitStack() as stack:
            files = request.httprequest.files.getlist('ufile')
            open_files = [stack.enter_context(io.BytesIO(file.read())) for file in files]

            # merge together data from existing prescriptions and from extra uploads
            prescription_id_index_map = {}
            current_index = len(open_files)
            for prescription in prescriptions:
                open_files.append(stack.enter_context(io.BytesIO(base64.b64decode(prescription.datas))))
                prescription_id_index_map[prescription.id] = current_index
                current_index += 1

            # update new_files structure with the new indices from prescriptions
            for new_file in new_files:
                for page in new_file['new_pages']:
                    if page.pop('old_file_type') == 'prescription':
                        page['old_file_index'] = prescription_id_index_map[page['old_file_index']]

            # apply the split/merge
            new_prescriptions = prescriptions._pdf_split(new_files=new_files, open_files=open_files, vals=vals)

        # archive original prescriptions if needed
        if archive == 'true':
            prescriptions.write({'active': False})

        response = request.make_response(json.dumps(new_prescriptions.ids), [('Content-Type', 'application/json')])
        return response

    @http.route(['/prescriptions/content/<int:id>'], type='http', auth='user')
    def prescriptions_content(self, id):
        return self._get_file_response(id)

    @http.route(['/prescriptions/pdf_content/<int:prescription_id>'], type='http', auth='user')
    def prescriptions_pdf_content(self, prescription_id):
        """
        This route is used to fetch the content of a pdf prescription to make it's thumbnail.
        404 not found is returned if the user does not haprescription_idve the rights to write on the prescription.
        """
        record = request.env['prescriptions.prescription'].browse(int(prescription_id))
        try:
            # We have to check that we can actually read the attachment as well.
            # Since we could have a prescription with an attachment linked to another record to which
            # we don't have access to.
            if record.attachment_id:
                record.attachment_id.check('read')
            record.check_access_rule('write')
        except AccessError:
            raise Forbidden()
        return self._get_file_response(prescription_id)

    @http.route(['/prescriptions/image/<int:res_id>',
                 '/prescriptions/image/<int:res_id>/<int:width>x<int:height>',
                 ], type='http', auth="public")
    def content_image(self, res_id=None, field='datas', share_id=None, width=0, height=0, crop=False, share_token=None, **kwargs):
        record = request.env['prescriptions.prescription'].browse(int(res_id))
        if share_id:
            share = request.env['prescriptions.share'].sudo().browse(int(share_id))
            record = share._get_prescriptions_and_check_access(share_token, [int(res_id)], operation='read')
        if not record or not record.exists():
            raise request.not_found()

        return request.env['ir.binary']._get_image_stream_from(
            record, field, width=int(width), height=int(height), crop=crop
        ).get_response()

    @http.route(['/prescription/zip'], type='http', auth='user')
    def get_zip(self, file_ids, zip_name, **kw):
        """route to get the zip file of the selection in the prescription's Kanban view (Prescription inspector).
        :param file_ids: if of the files to zip.
        :param zip_name: name of the zip file.
        """
        ids_list = [int(x) for x in file_ids.split(',')]
        prescriptions = request.env['prescriptions.prescription'].browse(ids_list)
        prescriptions.check_access_rights('read')
        response = self._make_zip(zip_name, prescriptions)
        return response

    @http.route(["/prescription/download/all/<int:share_id>/<access_token>"], type='http', auth='public')
    def share_download_all(self, access_token=None, share_id=None):
        """
        :param share_id: id of the share, the name of the share will be the name of the zip file share.
        :param access_token: share access token
        :returns the http response for a zip file if the token and the ID are valid.
        """
        env = request.env
        try:
            share = env['prescriptions.share'].sudo().browse(share_id)
            prescriptions = share._get_prescriptions_and_check_access(access_token, operation='read')
            if not prescriptions:
                raise request.not_found()
            streams = (
                self._get_share_zip_data_stream(share, prescription)
                for prescription in prescriptions
            )
            return self._generate_zip((share.name or 'unnamed-link') + '.zip', streams)
        except Exception:
            logger.exception("Failed to zip share link id: %s" % share_id)
        raise request.not_found()

    @classmethod
    def _get_share_zip_data_stream(cls, share, prescription):
        if prescription == cls._get_downloadable_prescriptions(prescription):
            return request.env['ir.binary']._get_stream_from(prescription, 'raw')
        return False

    @http.route([
        "/prescription/avatar/<int:share_id>/<access_token>",
        "/prescription/avatar/<int:share_id>/<access_token>/<prescription_id>",
    ], type='http', auth='public')
    def get_avatar(self, access_token=None, share_id=None, prescription_id=None):
        """
        :param share_id: id of the share.
        :param access_token: share access token
        :returns the picture of the share author for the front-end view.
        """
        try:
            env = request.env
            share = env['prescriptions.share'].sudo().browse(share_id)
            if share._get_prescriptions_and_check_access(access_token, prescription_ids=[], operation='read') is not False:
                if prescription_id:
                    user = env['prescriptions.prescription'].sudo().browse(int(prescription_id)).owner_id
                    if not user:
                        return env['ir.binary']._placeholder()
                else:
                    user = share.create_uid
                return request.env['ir.binary']._get_stream_from(user, 'avatar_128').get_response()
            else:
                return request.not_found()
        except Exception:
            logger.exception("Failed to download portrait")
        return request.not_found()

    @http.route(["/prescription/thumbnail/<int:share_id>/<access_token>/<int:id>"],
                type='http', auth='public')
    def get_thumbnail(self, id=None, access_token=None, share_id=None):
        """
        :param id:  id of the prescription
        :param access_token: token of the share link
        :param share_id: id of the share link
        :return: the thumbnail of the prescription for the portal view.
        """
        try:
            thumbnail = self._get_file_response(id, share_id=share_id, share_token=access_token, field='thumbnail')
            return thumbnail
        except Exception:
            logger.exception("Failed to download thumbnail id: %s" % id)
        return request.not_found()

    # single file download route.
    @http.route(["/prescription/download/<int:share_id>/<access_token>/<int:prescription_id>"],
                type='http', auth='public')
    def download_one(self, prescription_id=None, access_token=None, share_id=None, preview=None, **kwargs):
        """
        used to download a single file from the portal multi-file page.

        :param id: id of the file
        :param access_token:  token of the share link
        :param share_id: id of the share link
        :return: a portal page to preview and download a single file.
        """
        try:
            prescription = self._get_file_response(prescription_id, share_id=share_id, share_token=access_token, field='raw', as_attachment=not bool(preview))
            return prescription or request.not_found()
        except Exception:
            logger.exception("Failed to download prescription %s" % id)

        return request.not_found()

    def _create_uploaded_prescriptions(self, files, share, folder, prescriptions_values=None):
        prescriptions_values = {
            'tag_ids': [Command.set(share.tag_ids.ids)],
            'partner_id': share.partner_id.id,
            'owner_id': share.owner_id.user_ids[0].id if share.owner_id.user_ids else share.create_uid.id,
            'folder_id': folder.id,
            **(prescriptions_values or {}),
        }
        prescriptions = request.env['prescriptions.prescription'].with_user(share.create_uid)
        max_upload_size = prescriptions.get_prescription_max_upload_limit()
        for file in files:
            data = file.read()
            if max_upload_size and len(data) > max_upload_size:
                # TODO return error when converted to json
                logger.exception("File is too large.")
                raise Exception
            prescription_dict = {
                'mimetype': file.content_type,
                'name': file.filename,
                'datas': base64.b64encode(data),
                **prescriptions_values,
            }
            prescriptions |= prescriptions.create(prescription_dict)
        return prescriptions

    # Upload file(s) route.
    @http.route(["/prescription/upload/<int:share_id>/<token>/",
                 "/prescription/upload/<int:share_id>/<token>/<int:prescription_id>"],
                type='http', auth='public', methods=['POST'], csrf=False)
    def upload_attachment(self, share_id, token, prescription_id=None, **kwargs):
        """
        Allows public upload if provided with the right token and share_Link.

        :param share_id: id of the share.
        :param token: share access token.
        :param prescription_id: id of a prescription request to directly upload its content
        :return if files are uploaded, recalls the share portal with the updated content.
        """
        share = http.request.env['prescriptions.share'].sudo().browse(share_id)
        if not share.can_upload or (not prescription_id and share.action != 'downloadupload'):
            return http.request.not_found()

        available_prescriptions = share._get_prescriptions_and_check_access(
            token, [prescription_id] if prescription_id else [], operation='write')
        folder = share.folder_id
        folder_id = folder.id or False
        button_text = share.name or _('Share link')
        chatter_message = Markup("""<b>%s</b> %s <br/>
                               <b>%s</b> %s <br/>
                               <a class="btn btn-primary" href="/web#id=%s&model=prescriptions.share&view_type=form" target="_blank">
                                  <b>%s</b>
                               </a>
                             """) % (
                _("File uploaded by:"),
                http.request.env.user.name,
                _("Link created by:"),
                share.create_uid.name,
                share_id,
                button_text,
            )
        Prescriptions = request.env['prescriptions.prescription']
        if prescription_id and available_prescriptions:
            if available_prescriptions.type != 'empty':
                return http.request.not_found()
            try:
                max_upload_size = Prescriptions.get_prescription_max_upload_limit()
                file = request.httprequest.files.getlist('requestFile')[0]
                data = file.read()
                if max_upload_size and (len(data) > int(max_upload_size)):
                    # TODO return error when converted to json
                    return logger.exception("File is too Large.")
                mimetype = file.content_type
                write_vals = {
                    'mimetype': mimetype,
                    'name': file.filename,
                    'type': 'binary',
                    'datas': base64.b64encode(data),
                }
            except Exception:
                logger.exception("Failed to read uploaded file")
            else:
                available_prescriptions.write(write_vals)
                available_prescriptions.message_post(body=chatter_message)
        elif not prescription_id and available_prescriptions is not False:
            try:
                prescriptions = self._create_uploaded_prescriptions(request.httprequest.files.getlist('files'), share, folder)
            except Exception:
                logger.exception("Failed to upload prescription")
            else:
                for prescription in prescriptions:
                    prescription.message_post(body=chatter_message)
                if share.activity_option:
                    prescriptions.prescriptions_set_activity(settings_record=share)
        else:
            return http.request.not_found()
        return Markup("""<script type='text/javascript'>
                    window.open("/prescription/share/%s/%s", "_self");
                </script>""") % (share_id, token)

    # Frontend portals #############################################################################

    # share portals route.
    @http.route(['/prescription/share/<int:share_id>/<token>'], type='http', auth='public')
    def share_portal(self, share_id=None, token=None):
        """
        Leads to a public portal displaying downloadable files for anyone with the token.

        :param share_id: id of the share link
        :param token: share access token
        """
        try:
            share = http.request.env['prescriptions.share'].sudo().browse(share_id)
            available_prescriptions = share._get_prescriptions_and_check_access(token, operation='read')
            if available_prescriptions is False:
                if share._check_token(token):
                    options = {
                        'expiration_date': share.date_deadline,
                        'author': share.create_uid.name,
                    }
                    return request.render('prescriptions.not_available', options)
                else:
                    return request.not_found()

            shareable_prescriptions = available_prescriptions.filtered(lambda r: r.type != 'url')
            options = {
                'name': share.name,
                'base_url': share.get_base_url(),
                'token': str(token),
                'upload': share.action == 'downloadupload',
                'share_id': str(share.id),
                'author': share.create_uid.name,
                'date_deadline': share.date_deadline,
                'prescription_ids': shareable_prescriptions,
            }
            if len(shareable_prescriptions) == 1 and shareable_prescriptions.type == 'empty':
                return request.render("prescriptions.prescription_request_page", options)
            elif share.type == 'domain':
                options.update(all_button='binary' in [prescription.type for prescription in shareable_prescriptions],
                               request_upload=share.action == 'downloadupload')
                return request.render('prescriptions.share_workspace_page', options)

            total_size = sum(prescription.file_size for prescription in shareable_prescriptions)
            options.update(file_size=total_size, is_files_shared=True)
            return request.render("prescriptions.share_files_page", options)
        except Exception:
            logger.exception("Failed to generate the multi file share portal")
        return request.not_found()
