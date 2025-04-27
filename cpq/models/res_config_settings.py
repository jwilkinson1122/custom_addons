from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cpq_hash_truncate = fields.Boolean(
        string="Truncate CPQ Configuration Hash",
        config_parameter='cpq.hash_truncate',
        help="If enabled, the configuration hash will be truncated (default 16 characters)."
    )
    cpq_hash_truncate_length = fields.Integer(
        string="Hash Truncate Length",
        config_parameter='cpq.hash_truncate_length',
        help="Length to truncate the configuration hash if truncation is enabled. Default is 16."
    )

    # cpq_enable_qr_scan = fields.Boolean(
    #     string="Enable QR Scan Workflow",
    #     config_parameter='cpq.enable_qr_scan'
    # )
