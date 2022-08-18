

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = "pod.request"

    contact_id = fields.Many2one(
        comodel_name="pod.contact", ondelete="cascade", index=True
    )

    @api.constrains("patient_id", "contact_id")
    def _check_patient_contact(self):
        if self.env.context.get("no_check_patient", False):
            return
        for record in self.filtered(lambda r: r.contact_id):
            if record.contact_id.patient_id != record.patient_id:
                raise ValidationError(
                    _("Inconsistency between patient and contact")
                )

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.contact_id)
        return res
