
from odoo import http, _
from odoo.exceptions import AccessError
from odoo.addons.prescriptions.controllers.prescriptions import ShareRoute

from odoo.http import request


class SpreadsheetShareRoute(ShareRoute):
    @http.route()
    def share_portal(self, share_id=None, token=None):
        share = request.env["prescriptions.share"].sudo().browse(share_id).exists()
        if share:
            prescriptions = share._get_prescriptions_and_check_access(token, operation="read")
            if prescriptions and len(prescriptions) == 1 and prescriptions.handler == "spreadsheet":
                return self.open_spreadsheet(share.freezed_spreadsheet_ids, token)
        return super().share_portal(share_id, token)

    @http.route(
        ["/prescription/spreadsheet/share/<int:share_id>/<token>/<int:prescription_id>"],
        type="http",
        auth="public",
        methods=["GET"],
    )
    def open_shared_spreadsheet(self, share_id, token, prescription_id):
        spreadsheet = (
            request.env["prescriptions.shared.spreadsheet"]
            .sudo()
            .search([("share_id", "=", share_id), ("prescription_id", "=", prescription_id)])
        )
        return self.open_spreadsheet(spreadsheet, token)

    @http.route()
    # pylint: disable=redefined-builtin
    def download_one(self, prescription_id=None, access_token=None, share_id=None, **kwargs):
        prescription = request.env["prescriptions.prescription"].sudo().browse(prescription_id).exists()
        if prescription.handler == "spreadsheet":
            share = request.env["prescriptions.share"].sudo().browse(share_id)
            available_prescription = share._get_prescriptions_and_check_access(
                access_token, operation="read"
            )
            if not available_prescription or prescription not in available_prescription:
                raise AccessError(_("You don't have access to this prescription"))
            spreadsheet = (
                request.env["prescriptions.shared.spreadsheet"]
                .sudo()
                .search(
                    [("prescription_id", "=", prescription.id), ("share_id", "=", share_id)],
                    limit=1,
                )
            )
            stream = request.env["ir.binary"]._get_stream_from(
                spreadsheet, "excel_export", filename=prescription.name
            )
            return stream.get_response()
        return super().download_one(prescription_id, access_token, share_id, **kwargs)

    @http.route(
        ["/prescription/spreadsheet/data/<int:spreadsheet_id>/<token>"],
        type="http",
        auth="public",
        methods=["GET"],
    )
    def get_shared_spreadsheet_data(self, spreadsheet_id, token):
        spreadsheet = (
            request.env["prescriptions.shared.spreadsheet"]
            .sudo()
            .browse(spreadsheet_id)
            .exists()
        )
        share = spreadsheet.share_id
        if not share:
            raise request.not_found()
        prescription = share._get_prescriptions_and_check_access(token, operation="read")
        if not prescription:
            raise AccessError(_("You don't have access to this prescription"))
        stream = request.env["ir.binary"]._get_stream_from(
            spreadsheet, "spreadsheet_binary_data"
        )
        return stream.get_response()

    def open_spreadsheet(self, spreadsheet, token):
        share = spreadsheet.share_id
        if not share:
            raise request.not_found()
        prescriptions = share._get_prescriptions_and_check_access(token, operation="read")
        if not prescriptions or spreadsheet.prescription_id not in prescriptions:
            raise AccessError(_("You don't have access to this prescription"))
        if request.env.user._is_internal():
            prescription_id = spreadsheet.prescription_id.id
            return request.redirect(
                f"/web#spreadsheet_id={prescription_id}&action=action_open_spreadsheet&access_token={token}&share_id={share.id}"
            )
        return request.render(
            "spreadsheet.public_spreadsheet_layout",
            {
                "spreadsheet_name": spreadsheet.prescription_id.name,
                "share": share,
                "session_info": request.env["ir.http"].session_info(),
                "props": {
                    "dataUrl": f"/prescription/spreadsheet/data/{spreadsheet.id}/{token}",
                    "downloadExcelUrl": f"/prescription/download/{share.id}/{token}/{spreadsheet.prescription_id.id}",
                },
            },
        )
