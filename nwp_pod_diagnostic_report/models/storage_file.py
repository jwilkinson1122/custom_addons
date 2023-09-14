

from odoo import fields, models


class StorageFile(models.Model):
    _inherit = "storage.file"

    file_type = fields.Selection(
        selection_add=[("diagnostic_report_image", "Diagnostic Report Image")]
    )
