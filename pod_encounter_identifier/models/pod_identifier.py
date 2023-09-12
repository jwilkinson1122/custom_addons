from odoo import api, models


class PodiatryNWPIdentifier(models.AbstractModel):
    _name = "pod.nwp.identifier"
    _description = "pod.nwp.identifier"

    @api.model
    def get_request_format(self):
        return self.env["ir.config_parameter"].sudo().get_param("pod.identifier")

    @api.model
    def _get_internal_identifier(self, vals):
        encounter_code = vals.get("encounter_id", False) or self.env.context.get(
            "default_encounter_id"
        )
        if encounter_code:
            encounter = self.env["pod.encounter"].browse(encounter_code)
            sequence = encounter.get_next_number_cb(self.get_request_format())
            return "{}-{}".format(encounter.internal_identifier, sequence)
        return False
