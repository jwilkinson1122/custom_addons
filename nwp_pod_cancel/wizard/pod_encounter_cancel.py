from odoo import fields, models


class PodiatryEncounterCancel(models.TransientModel):
    _name = "pod.encounter.cancel"
    _description = "pod.encounter.cancel"

    encounter_id = fields.Many2one("pod.encounter")
    cancel_reason_id = fields.Many2one(
        "pod.cancel.reason", required=True, string="Cancel reason"
    )
    cancel_reason = fields.Text(string="Description")
    pos_session_id = fields.Many2one("pos.session", required=True)

    def run(self):
        self.ensure_one()
        return self.encounter_id.cancel(
            self.cancel_reason_id,
            session=self.pos_session_id,
            cancel_reason=self.cancel_reason,
        )
