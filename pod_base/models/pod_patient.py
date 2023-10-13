

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class PodiatryPatient(models.Model):
    # FHIR Entity: Patient (http://hl7.org/fhir/patient.html)
    _name = "pod.patient"
    _description = "Podiatry Patient"
    _inherit = ["pod.abstract", "mail.thread", "mail.activity.mixin"]
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        "res.partner", required=True, ondelete="restrict"
    )

    primary_practitioner_id = fields.Many2one(
        string="Primary Practitioner",
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
    )
    other_practitioner_ids = fields.Many2many(
        string="Other Practitioners",
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
    )
    
    partner_relation_label = fields.Char('Partner relation label', translate=True, default='Responsible:', readonly=True)
    
    patient_flag_ids = fields.One2many("pod.flag", inverse_name="patient_id")
    patient_flag_count = fields.Integer(compute="_compute_patient_flag_count")
    
    gender = fields.Selection([("male", "Male"), ("female", "Female"), ("other", "Other")])  
    birth_date = fields.Date(string="Birth date")  # FHIR Field: birthDate
    patient_age = fields.Integer(compute="_compute_age")

    @api.depends("birth_date")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.birth_date:
                age = relativedelta(
                    fields.Date.today(), record.birth_date
                ).years
            record.patient_age = age
            
    @api.depends("patient_flag_ids")
    def _compute_patient_flag_count(self):
        for rec in self:
            rec.patient_flag_count = len(rec.patient_flag_ids.ids)

    def action_view_patient_flags(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id("pod_base.pod_flag_action")
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = "[('patient_id', '=', " + str(self.id) + ")]"
        if len(self.patient_flag_ids) == 1:
            res = self.env.ref("pod.flag.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.patient_flag_ids.id
        return result

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].sudo().next_by_code("pod.patient")
            or "/"
        )

    def open_parent(self):
        """Utility method used to add an "Open Parent" button in partner
        views"""
        self.ensure_one()
        address_form_id = self.env.ref("base.view_partner_address_form").id
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "form",
            "views": [(address_form_id, "form")],
            "res_id": self.parent_id.id,
            "target": "new",
            "flags": {"form": {"action_buttons": True}},
        }
