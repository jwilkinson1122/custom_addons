# See LICENSE file for full copyright and licensing details.


from odoo import _, models
from odoo.exceptions import ValidationError


class CloseReasonAccounts(models.TransientModel):
    _inherit = "close.reason"

    def save_close(self):
        """Override method to raise warning when accounts payment of patient is
        remaining when patient is closed"""
        patient = self._context.get("active_id")
        patient_rec = self.env["patient.patient"].browse(patient)
        if self.env["patient.payslip"].search(
            [
                ("patient_id", "=", patient_rec.id),
                ("state", "in", ["confirm", "pending"]),
            ]
        ):
            raise ValidationError(
                _(
                    "You can't close patient because payment of accounts of "
                    "patient is remaining!"
                )
            )
        return super(CloseReasonAccounts, self).save_close()
