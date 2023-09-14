# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PodiatryDeviceRequest(models.Model):
    # FHIR entity: Device request
    # (https://www.hl7.org/fhir/devicerequest.html)
    _name = "pod.device.request"
    _description = "Podiatry Device request"
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
        domain=[("is_device", "=", True)],
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
    device_administration_ids = fields.One2many(
        comodel_name="pod.device.administration",
        inverse_name="device_request_id",
    )
    device_administration_count = fields.Integer(
        compute="_compute_device_administration_count",
        string="# of Device Administration Requests",
        copy=False,
        default=0,
    )

    @api.depends("device_administration_ids")
    def _compute_device_administration_count(self):
        for rec in self:
            rec.device_administration_count = len(
                rec.device_administration_ids
            )

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"]
            .sudo()
            .next_by_code("pod.device.request")
            or "/"
        )

    def _get_event_values(self):
        return {
            "device_request_id": self.id,
            "product_id": self.product_id.id,
            "qty": self.qty,
            "product_uom_id": self.product_uom_id.id,
            "patient_id": self.patient_id.id,
            "name": self.name,
        }

    def generate_event(self):
        self.ensure_one()
        return self.env["pod.device.administration"].create(
            self._get_event_values()
        )

    def action_view_device_administration(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_device_request."
            "pod_device_administration_action"
        )
        result["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_device_request_id": self.id,
            "default_name": self.name,
            "default_product_id": self.product_id.id,
            "default_product_uom_id": self.product_uom_id.id,
            "default_qty": self.qty,
        }
        result["domain"] = (
            "[('device_request_id', '=', " + str(self.id) + ")]"
        )
        if len(self.device_administration_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.device_administration_ids.id
        return result

    def _get_parent_field_name(self):
        return "device_request_id"

    def action_view_request_parameters(self):
        return {
            "view": "pod_device_request."
            "pod_device_request_action",
            "view_form": "pod.device.request.view.form",
        }

    @api.constrains("patient_id")
    def _check_patient_device(self):

        if not self.env.context.get("no_check_patient", False):
            if self.device_administration_ids.filtered(
                lambda r: r.patient_id != self.patient_id
            ):
                raise ValidationError(_("Patient inconsistency"))
