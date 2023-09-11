from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# FHIR entity: Prescription request
# (https://www.hl7.org/fhir/prescriptionrequest.html)

class PodiatryPrescriptionRequest(models.Model):
    _name = "pod.prescription.request"
    _description = "Podiatry Prescription request"
    _inherit = "pod.request"

    category = fields.Selection(
        [
            ("inpatient", "Inpatient"),
            ("outpatient", "Outpatient"),
            ("community", "Community"),
        ],
        required=True,
        default="inpatient",
    )  # FHIR Field: category
    product_id = fields.Many2one(
        comodel_name="product.product",
        domain=[("is_prescription", "=", True)],
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        index=True,
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        index=True,
    )
    qty = fields.Float(
        default=1.0,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    prescription_administration_ids = fields.One2many(
        comodel_name="pod.prescription.administration",
        inverse_name="prescription_request_id",
    )
    prescription_administration_count = fields.Integer(
        compute="_compute_prescription_administration_count",
        string="# of Prescription Administration Requests",
        copy=False,
        default=0,
    )

    @api.depends("prescription_administration_ids")
    def _compute_prescription_administration_count(self):
        for rec in self:
            rec.prescription_administration_count = len(
                rec.prescription_administration_ids
            )

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"]
            .sudo()
            .next_by_code("pod.prescription.request")
            or "/"
        )

    def _get_event_values(self):
        return {
            "prescription_request_id": self.id,
            "product_id": self.product_id.id,
            "qty": self.qty,
            "product_uom_id": self.product_uom_id.id,
            "patient_id": self.patient_id.id,
            "name": self.name,
        }

    def generate_event(self):
        self.ensure_one()
        return self.env["pod.prescription.administration"].create(
            self._get_event_values()
        )

    def action_view_prescription_administration(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_prescription_request."
            "pod_prescription_administration_action"
        )
        result["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_prescription_request_id": self.id,
            "default_name": self.name,
            "default_product_id": self.product_id.id,
            "default_product_uom_id": self.product_uom_id.id,
            "default_qty": self.qty,
        }
        result["domain"] = (
            "[('prescription_request_id', '=', " + str(self.id) + ")]"
        )
        if len(self.prescription_administration_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.prescription_administration_ids.id
        return result

    def _get_parent_field_name(self):
        return "prescription_request_id"

    def action_view_request_parameters(self):
        return {
            "view": "pod_prescription_request."
            "pod_prescription_request_action",
            "view_form": "pod.prescription.request.view.form",
        }

    @api.constrains("patient_id")
    def _check_patient_prescription(self):

        if not self.env.context.get("no_check_patient", False):
            if self.prescription_administration_ids.filtered(
                lambda r: r.patient_id != self.patient_id
            ):
                raise ValidationError(_("Patient inconsistency"))
