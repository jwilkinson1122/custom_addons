

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    prescription_ids = fields.One2many(
        comodel_name="prescription",
        inverse_name="partner_id",
        string="Prescription",
    )
    prescription_count = fields.Integer(
        string="Prescription count",
        compute="_compute_prescription_count",
    )

    def _compute_prescription_count(self):
        prescription_data = self.env["prescription"].read_group(
            [("partner_id", "in", self.ids)], ["partner_id"], ["partner_id"]
        )
        mapped_data = {r["partner_id"][0]: r["partner_id_count"] for r in prescription_data}
        for record in self:
            record.prescription_count = mapped_data.get(record.id, 0)

    def action_view_prescription(self):
        self.ensure_one()
        action = self.sudo().env.ref("prescription.prescription_action").read()[0]
        prescription = self.prescription_ids
        if len(prescription) == 1:
            action.update(
                res_id=prescription.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
        else:
            action["domain"] = [("partner_id", "in", self.ids)]
        return action
