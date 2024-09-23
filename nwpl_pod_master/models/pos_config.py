from odoo import api, fields, models, _
from odoo.exceptions import UserError

# class PosConfig(models.Model):
#     _inherit = 'pos.config'

#     @api.model
#     def write(self, vals):
#         active_sessions = self.env['pos.session'].search([('config_id', 'in', self.ids), ('state', '!=', 'closed')])
#         if 'limit_categories' in vals and active_sessions:
#             raise UserError(_("You can't modify Restrict Categories while a session is open. Please close all active sessions first."))
#         return super(PosConfig, self).write(vals)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    def close_sessions_and_update(self, vals):
        sessions_to_close = self.env['pos.session'].search([('config_id', 'in', self.ids), ('state', '!=', 'closed')])
        for session in sessions_to_close:
            session.action_pos_session_closing_control()  # Automatically close the session
        return super(PosConfig, self).write(vals)
