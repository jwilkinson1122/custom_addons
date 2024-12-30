from odoo import fields, models


class SaleOrderVersionRestoreWizard(models.TransientModel):
    _name = 'sale.order.version.restore.wizard'
    _description = 'Sale Order Version Restore Wizard'

    version_id = fields.Many2one('sale.order.version', string='Version', required=True)

    def action_confirm(self):
        result = self.version_id.restore_order()
        return result

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}