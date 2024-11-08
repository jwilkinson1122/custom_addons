from odoo import api, fields, models


class FileTestConnection(models.TransientModel):
    _name = "file.test.connection"
    _description = "File Test Connection Wizard"

    def _get_check_connection_method_selection(self):
        return self.env["file.storage"]._get_check_connection_method_selection()

    storage_id = fields.Many2one("file.storage")
    check_connection_method = fields.Selection(
        selection="_get_check_connection_method_selection",
        required=True,
    )

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        res["storage_id"] = self.env.context.get("active_id", False)
        return res

    def action_test_config(self):
        return self.storage_id._test_config(self.check_connection_method)
