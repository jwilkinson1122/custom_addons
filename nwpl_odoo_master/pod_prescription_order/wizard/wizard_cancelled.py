from odoo import models, fields, api, exceptions, _

class CancelledWorkOrderWizard(models.TransientModel):
    _name = "cancelled.wo"
    _description = "Cancel Work Order Wizard"

    note = fields.Text('Note')

    def cancelled(self):
        work_order = self.env['prescription.work_order'].browse(self.env.context.get('active_id'))
        work_order.write({'note': self.note, 'state': 'cancelled'})
