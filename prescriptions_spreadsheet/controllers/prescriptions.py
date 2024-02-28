# -*- coding: utf-8 -*-

from odoo import _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.prescriptions.controllers.prescriptions import ShareRoute

class SpreadsheetShareRoute(ShareRoute):

    @classmethod
    def _get_downloadable_prescriptions(cls, prescriptions):
        """
            override of prescriptions to prevent the download
            of spreadsheets binary as they are not usable
        """
        return super()._get_downloadable_prescriptions(prescriptions.filtered(lambda doc: doc.mimetype != "application/o-spreadsheet"))

    def _create_uploaded_prescriptions(self, *args, **kwargs):
        prescriptions = super()._create_uploaded_prescriptions(*args, **kwargs)
        if any(doc.handler == "spreadsheet" for doc in prescriptions):
            raise AccessError(_("You cannot upload spreadsheets in a shared folder"))
        return prescriptions

    @classmethod
    def _get_share_zip_data_stream(cls, share, prescription):
        if prescription.handler == "spreadsheet":
            spreadsheet_copy = share.freezed_spreadsheet_ids.filtered(
                lambda s: s.prescription_id == prescription
            )
            try:
                return request.env["ir.binary"]._get_stream_from(
                    spreadsheet_copy, "excel_export", filename=prescription.name
                )
            except MissingError:
                return False
        return super()._get_share_zip_data_stream(share, prescription)
