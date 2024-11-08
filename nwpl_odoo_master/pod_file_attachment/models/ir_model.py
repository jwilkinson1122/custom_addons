from odoo import fields, models


class IrModel(models.Model):

    _inherit = "ir.model"

    storage_id = fields.Many2one(
        "file.storage",
        help="If specified, all attachments linked to this model will be "
        "stored in the provided storage.",
    )
