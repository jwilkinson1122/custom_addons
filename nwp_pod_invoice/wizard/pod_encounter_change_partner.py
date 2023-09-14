from odoo import fields, models


class PodiatryEncounterChangePartner(models.TransientModel):
    _name = "pod.encounter.change.partner"
    _description = "pod.encounter.change.partner"

    partner_id = fields.Many2one("res.partner", required=True)
    encounter_id = fields.Many2one("pod.encounter", required=True)

    def run(self):
        self.encounter_id._change_invoice_partner(self.partner_id)
        return True
