

from odoo import models, fields


class PrescriptionSpreadsheetShare(models.Model):
    _name = 'prescriptions.shared.spreadsheet'
    _inherit = 'spreadsheet.mixin'
    _description = 'Copy of a shared spreadsheet'

    share_id = fields.Many2one('prescriptions.share', required=True, ondelete='cascade')
    prescription_id = fields.Many2one('prescriptions.prescription', required=True, ondelete='cascade')
    excel_export = fields.Binary()

    _sql_constraints = [
        ('_unique', 'unique(share_id, prescription_id)', "Only one freezed spreadsheet per prescription share"),
    ]
