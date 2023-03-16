# -*- coding: utf-8 -*-
# Import packages & Support files
from odoo import models, fields, api
from . import s3_constants
from . import s3
import logging
import base64


#############################################################################
#                     Defined S3 Credentials Model
#############################################################################


class S3Credentials(models.Model):
    _name = s3_constants.S3_CREDENTIALS_MODEL

    access_key = fields.Char(string="AccessKey ID", required=True,
                             default=lambda self: self._get_default_access_key())
    secret_key = fields.Char(string="AccessSecret Key", required=True,
                             default=lambda self: self._get_default_secret_key())
    bucket = fields.Char(string="S3 Bucket", required=True,
                         default=lambda self: self._get_default_bucket())

    #################################################################################
    # This method revoke on button click event and perform following actions     ####
    # a. Add Credentials to database models                                      ####
    #################################################################################

    def connect(self):
        _logging = logging.getLogger(__name__)
        rep_message = ''
        val_struct = {
            'access_key': self.access_key,
            'secret_key': self.secret_key,
            'bucket': self.bucket
        }

        try:
            # Create db cursor and query to check existence of record
            db_cursor = self.env[self._name]
            db_rows = db_cursor.search([])
            if db_rows and len(db_rows) > 0:
                _logging.info("Update CRD record")
                db_rows[s3_constants.DEFAULT_INDEX].access_key = val_struct["access_key"]
                db_rows[s3_constants.DEFAULT_INDEX].secret_key = val_struct["secret_key"]
                db_rows[s3_constants.DEFAULT_INDEX].bucket = val_struct["bucket"]
                db_cursor.update(db_rows[s3_constants.DEFAULT_INDEX])
                rep_message += s3_constants.CREDENTIAL_UPDATE_MSG
            else:
                _logging.info("Create CRD record")
                super().create(val_struct)
                rep_message += s3_constants.CREDENTIAL_SAVE_MSG

        except Exception as ex:
            _logging.exception("Exception CRD: " + str(ex))
            rep_message += s3_constants.CREDENTIAL_EXCEPT_MSG
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': s3_constants.FAILURE_POP_UP_TITLE,
                'message': rep_message,
                'sticky': False,
            }
        }

    def get_s3_credentials(self):
        cred_response = {}
        try:
            db_cursor = self.env[self._name]
            db_rows = db_cursor.search([])
            if db_rows and len(db_rows) > 0:
                cred_response["access_key"] = db_rows[s3_constants.DEFAULT_INDEX].access_key
                cred_response["secret_key"] = db_rows[s3_constants.DEFAULT_INDEX].secret_key
                cred_response["bucket"] = db_rows[s3_constants.DEFAULT_INDEX].bucket
            else:
                cred_response["err_message"] = s3_constants.CREDENTIAL_NOT_FND_MSG
                cred_response["error"] = "Credentials are not found"
        except Exception as ex:
            cred_response["error"] = str(ex)
            cred_response["err_message"] = s3_constants.CREDENTIAL_EXCEPT_FETCH_MSG
        return cred_response

    @api.model
    def _get_default_access_key(self):
        latest_record = self.env[s3_constants.S3_CREDENTIALS_MODEL].search([])
        return latest_record[s3_constants.DEFAULT_INDEX].access_key if len(latest_record) > 0 else ''

    @api.model
    def _get_default_secret_key(self):
        latest_record = self.env[s3_constants.S3_CREDENTIALS_MODEL].search([])
        return latest_record[s3_constants.DEFAULT_INDEX].secret_key if len(latest_record) > 0 else ''

    @api.model
    def _get_default_bucket(self):
        latest_record = self.env[s3_constants.S3_CREDENTIALS_MODEL].search([])
        return latest_record[s3_constants.DEFAULT_INDEX].bucket if len(latest_record) > 0 else ''


class S3Connect(models.Model):
    _inherit = s3_constants.CONTACT_MODEL
    attachment_ids = fields.Many2many(s3_constants.IR_ATTACHMENT_MODEL,
                                      s3_constants.CLASS_IR_ATTACHMENT_REL_MODEL,
                                      'class_id',
                                      'attachment_id',
                                      'Attachments')

    def s3_upload_btn(self):
        _log = logging.getLogger(__name__)
        pop_message = ""

        r_partner = self.env[s3_constants.CONTACT_MODEL].search([('id', '=', self.id)])
        file_records = {
                        'res_partner_id': self.id,
                        'res_name': r_partner.name,
                        'files': []
                    }
        for attachment in self.attachment_ids:
            try:
                decoded_data = base64.b64decode(attachment.datas)
                temp = {
                    "id": attachment.id,
                    "name": attachment.name,
                    "mimetype": attachment.mimetype,
                    "db_datas": decoded_data
                }
                file_records["files"].append(temp)
            except Exception as ex:
                _log.exception("Log >> File attachment info: " + str(ex))

        if len(file_records["files"]) > 0:
            credentials = self.env[s3_constants.S3_CREDENTIALS_MODEL].get_s3_credentials()
            _log.info(credentials)
            if 'error' not in credentials and 'err_message' not in credentials:
                _s3 = s3.S3(aws_credential=credentials)
                _sp_response = _s3.export_documents(res_data=file_records)
                if not _sp_response["err_status"]:
                    pop_message += "Files uploaded successfully: " + s3_constants.AWS_S3_OPT_KEY
                else:
                    pop_message += str(_sp_response["response"])
            else:
                pop_message += credentials["err_message"]
        else:
            pop_message += s3_constants.AWS_S3_FILE_NOT_FND
            
        if s3_constants.AWS_S3_OPT_KEY in pop_message:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "System Notification",
                    'message': pop_message,
                    'sticky': False,
                }
            }

    def s3_download_btn(self):
        _log = logging.getLogger(__name__)
        pop_message = ""

        r_partner = self.env[s3_constants.CONTACT_MODEL].search([('id', '=', self.id)])
        credentials = self.env[s3_constants.S3_CREDENTIALS_MODEL].get_s3_credentials()

        if 'error' not in credentials and 'err_message' not in credentials:
            _s3 = s3.S3(aws_credential=credentials)
            _sp_response = _s3.import_documents(
                db_cursor=self.env.cr, user_rcd=r_partner, self_env=self.env
            )
            if not _sp_response["err_status"]:
                pop_message += "Files downloaded successfully: " + s3_constants.AWS_S3_OPT_KEY
            else:
                pop_message += str(_sp_response["response"])
        else:
            pop_message += credentials["err_message"]
        if s3_constants.AWS_S3_OPT_KEY in pop_message:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "System Notification",
                    'message': pop_message,
                    'sticky': False,
                }
            }
