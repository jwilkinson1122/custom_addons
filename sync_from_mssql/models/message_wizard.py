
from odoo import models, fields, _, api,tools
class MessageWizard(models.TransientModel):
    _name = 'message.wizard'
    _description = 'Message Wizard'
    message = fields.Text('message', required=True)

 
    #@api.multi
    def action_confirm(self):
        return {'type': 'ir.actions.act_window_close'}