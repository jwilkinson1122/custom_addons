from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError

# FHIR Entity: Procedure request
# (https://www.hl7.org/fhir/procedurerequest.html)

class PodiatryProcedureRequest(models.Model):
    _name = "pod.procedure.request"
    _description = "Procedure Request"
    _inherit = "pod.request"
    _order = "sequence, id"

    internal_identifier = fields.Char(string="Procedure request")
    sequence = fields.Integer(
        required=True,
        default=1,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    occurrence = fields.Datetime(
        string="Occurrence date",
        help="When the procedure should occur",
        required=True,
        default=fields.Datetime.now,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    procedure_request_ids = fields.One2many(
        inverse_name="procedure_request_id"
    )
    procedure_ids = fields.One2many(
        string="Related Procedure",
        comodel_name="pod.procedure",
        inverse_name="procedure_request_id",
        readonly=True,
    )
    procedure_count = fields.Integer(
        compute="_compute_procedure_count",
        string="# of Procedures",
        copy=False,
    )

    @api.depends("procedure_ids")
    def _compute_procedure_count(self):
        for record in self:
            record.procedure_count = len(record.procedure_ids)

    def unlink(self):
        if self.mapped("procedure_ids"):
            raise exceptions.Warning(
                _("You cannot delete a record that refers to a Procedure!")
            )
        return super(PodiatryProcedureRequest, self).unlink()

    def active2completed(self):
        self.filtered(lambda r: not r.procedure_ids).generate_event()
        return super().active2completed()

    def action_view_procedure(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_clinical_procedure.pod_procedure_action"
        )
        result["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_performer_id": self.performer_id.id,
            "default_procedure_request_id": self.id,
            "default_name": self.name,
        }
        result["domain"] = (
            "[('procedure_request_id', '=', " + str(self.id) + ")]"
        )
        if len(self.procedure_ids) == 1:
            res = self.env.ref("pod.procedure.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.procedure_ids.id
        return result

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"]
            .sudo()
            .next_by_code("pod.procedure.request")
            or "/"
        )

    def _get_procedure_values(self):
        self.ensure_one()
        return {
            "procedure_request_id": self.id,
            "name": self.name,
            "plan_definition_id": (
                self.plan_definition_id and self.plan_definition_id.id
            ),
            "activity_definition_id": (
                self.activity_definition_id and self.activity_definition_id.id
            ),
            "plan_definition_action_id": (
                self.plan_definition_action_id
                and self.plan_definition_action_id.id
            ),
            "service_id": self.service_id and self.service_id.id,
            "patient_id": self.patient_id.id,
            "performer_id": self.performer_id and self.performer_id.id,
        }

    def generate_event(self):
        proc_obj = self.env["pod.procedure"]
        procedure_ids = []
        for request in self:
            vals = request._get_procedure_values()
            procedure = proc_obj.create(vals)
            procedure_ids.append(procedure.id)
        return proc_obj.browse(procedure_ids)

    def _get_parent_field_name(self):
        return "procedure_request_id"

    def action_view_request_parameters(self):
        return {
            "view": "pod_clinical_procedure.pod_procedure_request_action",
            "view_form": "pod.procedure.request.view.form",
        }

    @api.constrains("patient_id")
    def _check_patient_procedure(self):
        if not self.env.context.get("no_check_patient", False):
            if self.procedure_request_id.filtered(
                lambda r: r.patient_id != self.patient_id
            ):
                raise ValidationError(_("Patient inconsistency"))
