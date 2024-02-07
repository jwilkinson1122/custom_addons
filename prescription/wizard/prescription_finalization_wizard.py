from odoo import fields, models


class PrescriptionFinalizationWizard(models.TransientModel):
    _name = "prescription.finalization.wizard"
    _description = "Prescription Finalization Wizard"

    finalization_id = fields.Many2one(
        comodel_name="prescription.finalization", string="Reason", required=True
    )

    def action_finish(self):
        self.ensure_one()
        prescription_ids = self.env.context.get("active_ids")
        prescription = self.env["prescription"].browse(prescription_ids)
        prescription.write({"finalization_id": self.finalization_id, "state": "finished"})
