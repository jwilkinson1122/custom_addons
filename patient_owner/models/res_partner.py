# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("patient_ids")
    def _compute_patient_count(self):
        for rec in self:
            rec.patient_count = len(rec.patient_ids)

    patient_ids = fields.One2many("patient", "partner_id", string="Patients")
    patient_count = fields.Integer(
        compute=_compute_patient_count, string="Number of Patients", store=True
    )

    def action_view_patients(self):
        xmlid = "patient.action_patient"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        if self.patient_count > 1:
            action["domain"] = [("id", "in", self.patient_ids.ids)]
        else:
            action["views"] = [(self.env.ref("patient.view_patient_form").id, "form")]
            action["res_id"] = self.patient_ids and self.patient_ids.ids[0] or False
        return action
