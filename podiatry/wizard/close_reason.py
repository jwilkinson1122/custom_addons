# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CloseReason(models.TransientModel):
    """Defining TransientModel to close reason."""

    _name = "close.reason"
    _description = "Close Reason"

    reason = fields.Text("Reason")

    def save_close(self):
        """Method to close patient and change state to close."""
        patient_rec = self.env["patient.patient"].browse(
            self._context.get("active_id")
        )
        patient_rec.write(
            {
                "state": "close",
                "close_reason": self.reason,
                "active": False,
            }
        )
        patient_rec.standard_id._compute_total_patient()
        for rec in self.env["patient.reminder"].search(
            [("pat_id", "=", patient_rec.id)]
        ):
            rec.active = False
        if patient_rec.partner_id:
            patient_rec.partner_id.active = False
