from odoo import api, fields, models


class PodiatryPatient(models.Model):
    _inherit = "pod.patient"

    pod_flag_ids = fields.One2many("pod.flag", inverse_name="patient_id")
    pod_flag_count = fields.Integer(compute="_compute_pod_flag_count")

    @api.depends("pod_flag_ids")
    def _compute_pod_flag_count(self):
        for rec in self:
            rec.pod_flag_count = len(rec.pod_flag_ids.ids)

    def action_view_flags(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_administration_flag.pod_flag_action"
        )
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = "[('patient_id', '=', " + str(self.id) + ")]"
        if len(self.pod_flag_ids) == 1:
            res = self.env.ref("pod.flag.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.pod_flag_ids.id
        return result
