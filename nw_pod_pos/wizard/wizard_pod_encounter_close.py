from odoo import fields, models


class WizardPodiatryEncounterClose(models.TransientModel):
    _name = "wizard.pod.encounter.close"
    _description = "wizard.pod.encounter.close"

    pos_session_id = fields.Many2one(
        comodel_name="pos.session",
        string="PoS Session",
        required=True,
        domain=[("state", "=", "opened")],
    )
    encounter_id = fields.Many2one(
        comodel_name="pod.encounter",
        string="encounter",
        readonly=True,
        required=True,
    )

    def run(self):
        self.ensure_one()
        # It could be changed if it need a finished option
        # self.encounter_id.pos_session_id = self.pos_session_id
        self.encounter_id.with_context(
            pos_session_id=self.pos_session_id.id,
            company_id=self.pos_session_id.config_id.company_id.id,
        ).inprogress2onleave()
