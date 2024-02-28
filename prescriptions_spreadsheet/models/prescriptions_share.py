

import base64
from odoo import api, Command, models, fields

class PrescriptionShare(models.Model):
    _inherit = "prescriptions.share"

    freezed_spreadsheet_ids = fields.One2many(
        "prescriptions.shared.spreadsheet", "share_id"
    )

    def _get_prescriptions_and_check_access(self, access_token, prescription_ids=None, operation="write"):
        available_prescriptions = super()._get_prescriptions_and_check_access(access_token, prescription_ids, operation)
        if operation == "write" and available_prescriptions and not self.env.user._is_internal():
            return available_prescriptions.filtered(lambda doc: doc.handler != "spreadsheet")
        return available_prescriptions

    @api.model
    def action_get_share_url(self, vals):
        if "spreadsheet_shares" in vals:
            spreadsheet_shares = vals.pop("spreadsheet_shares")
            create_commands = self._create_spreadsheet_share_commands(spreadsheet_shares)
            vals["freezed_spreadsheet_ids"] = create_commands
        return super().action_get_share_url(vals)

    @api.model
    def open_share_popup(self, vals):
        if "spreadsheet_shares" in vals:
            spreadsheet_shares = vals.pop("spreadsheet_shares")
            create_commands = self._create_spreadsheet_share_commands(spreadsheet_shares)
            vals["freezed_spreadsheet_ids"] = create_commands
        return super().open_share_popup(vals)

    def _create_spreadsheet_share_commands(self, spreadsheet_shares):
        create_commands = []
        for share in spreadsheet_shares:
            excel_zip = self.env["spreadsheet.mixin"]._zip_xslx_files(
                share["excel_files"]
            )
            create_commands.append(
                Command.create(
                    {
                        "prescription_id": share["prescription_id"],
                        "spreadsheet_data": share["spreadsheet_data"],
                        "excel_export": base64.b64encode(excel_zip),
                    }
                )
            )
        return create_commands
