from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# FHIR Entity: Procedure request
# (https://www.hl7.org/fhir/procedurerequest.html)

class PodiatryLaboratoryRequest(models.Model):
    # _inherit = "pod.laboratory.request"
    _name = "pod.laboratory.request"
    _description = "Laboratory Request"
    _inherit = "pod.request"

    
    internal_identifier = fields.Char(string="Laboratory request")

    laboratory_service_ids = fields.Many2many("pod.laboratory.service", readonly=True)
    
    # laboratory_event_ids = fields.One2many(
    #     string="Laboratory Events",
    #     states={"draft": [("readonly", False)], "active": [("readonly", False)],})
    
    laboratory_event_ids = fields.One2many(
        string="Laboratory Events",
        comodel_name="pod.laboratory.event",
        inverse_name="laboratory_request_id",
        states={"draft": [("readonly", False)], "active": [("readonly", False)],},
        readonly=True,
    )
    
    laboratory_event_count = fields.Integer(
        compute="_compute_laboratory_event_count",
        string="# of Events",
        copy=False,
    )
    
    event_coverage_agreement_id = fields.Many2one(
        "pod.coverage.agreement",
        compute="_compute_event_coverage_agreement_id",
    )

    
    @api.depends("laboratory_event_ids")
    def _compute_laboratory_event_count(self):
        for rec in self:
            rec.laboratory_event_count = len(rec.laboratory_event_ids.ids)

    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("pod.laboratory.request") or "/"

    def _get_parent_field_name(self):
        return "laboratory_request_id"

    def action_view_request_parameters(self):
        return {
            "view": "pod_clinical_laboratory.pod_laboratory_request_action",
            "view_form": "pod.procedure.request.view.form",
        }

    def _get_event_values(self, vals=False):
        result = {
            "performer_id": self.performer_id.id or False,
            "service_id": self.service_id.id or False,
        }
        result.update(vals or {})
        result.update(
            {
                "laboratory_request_id": self.id,
                "patient_id": self.patient_id.id,
            }
        )
        return result

    def generate_event(self, vals=False):
        self.ensure_one()
        return self.env["pod.laboratory.event"].create(self._get_event_values(vals))

    def action_view_laboratory_events(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_clinical_laboratory.pod_laboratory_event_action"
        )
        result["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_performer_id": self.performer_id.id,
            "default_laboratory_request_id": self.id,
            "default_name": self.name,
        }
        result["domain"] = "[('laboratory_request_id', '=', " + str(self.id) + ")]"
        if len(self.laboratory_event_ids) == 1:
            res = self.env.ref("pod.laboratory.event.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.laboratory_event_ids.id
        return result

    @api.constrains("patient_id")
    def _check_patient_events(self):
        if not self.env.context.get("no_check_patient", False):
            if self.laboratory_event_ids.filtered(
                lambda r: r.patient_id != self.patient_id
            ):
                raise ValidationError(_("Patient inconsistency"))

    
    @api.depends("service_id", "coverage_id.coverage_template_id", "center_id")
    def _compute_event_coverage_agreement_id(self):
        for record in self:
            cai = self.env["pod.coverage.agreement.item"].get_item(
                record.service_id,
                record.coverage_id.coverage_template_id,
                record.center_id,
            )
            agreement = self.env["pod.coverage.agreement"]
            if cai:
                agreement = cai.coverage_agreement_id
            record.event_coverage_agreement_id = agreement
