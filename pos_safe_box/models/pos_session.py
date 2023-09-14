from odoo import fields, models


class PosSession(models.Model):
    _inherit = "pos.session"

    pos_session_validation_id = fields.Many2one("pos.session.validation", readonly=True)

    def action_pos_session_close(self):
        res = super(PosSession, self).action_pos_session_close()
        for session in self:
            sbg = session.config_id.safe_box_group_id
            if sbg:
                self.pos_session_validation_id = sbg.get_current_session_validation()
        return res
