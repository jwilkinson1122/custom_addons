from odoo import fields, models


class IrModelFields(models.Model):

    _inherit = "ir.model.fields"

    storage_id = fields.Many2one(
        "file.storage",
        help="If specified, all attachments linked to this field will be "
        "stored in the provided storage.",
    )
