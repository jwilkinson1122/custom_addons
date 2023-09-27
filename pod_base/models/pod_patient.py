

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
    
    pod_location_primary_id = fields.Many2one(
        string="Primary Podiatry Practice",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )
    pod_location_secondary_ids = fields.Many2many(
        string="Secondary Podiatry Practices",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )

    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")]
    )  # FHIR Field: gender
    # https://www.hl7.org/fhir/valueset-administrative-gender.html)
    marital_status = fields.Selection(
        [
            ("s", "Single"),
            ("m", "Married"),
            ("w", "Widowed"),
            ("d", "Divorced"),
            ("l", "Separated"),
        ]
    )  # FHIR Field: maritalStatus
    # https://www.hl7.org/fhir/valueset-marital-status.html
    birth_date = fields.Date(string="Birth date")  # FHIR Field: birthDate
    deceased_date = fields.Date(
        string="Deceased date"
    )  # FHIR Field: deceasedDate
    is_deceased = fields.Boolean(
        compute="_compute_is_deceased"
    )  # FHIR Field: deceasedBoolean
    patient_age = fields.Integer(compute="_compute_age")

    @api.depends("deceased_date")
    def _compute_is_deceased(self):
        for record in self:
            record.is_deceased = bool(record.deceased_date)

    @api.depends("birth_date")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.birth_date:
                age = relativedelta(
                    fields.Date.today(), record.birth_date
                ).years
            record.patient_age = age

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
