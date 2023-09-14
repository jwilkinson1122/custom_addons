

from odoo import api, fields, models


class PodiatryClinicalImpression(models.Model):

    _name = "pod.clinical.impression"
    _inherit = ["pod.event", "mail.thread", "mail.activity.mixin"]
    _description = "Podiatry Clinical Impression"
    _conditions = "condition_ids"
    _order = "validation_date desc, id"
    _rec_name = "internal_identifier"

    @api.model
    def _get_states(self):
        return {
            "in_progress": ("In Progress", "draft"),
            "completed": ("Completed", "done"),
            "cancelled": ("Cancelled", "done"),
        }

    fhir_state = fields.Selection(default="in_progress", readonly=True)

    specialty_id = fields.Many2one(
        "pod.specialty", required=True, readonly=True
    )
    # FHIR code: type of clinical assessment performed.
    # TODO: add domain, so a partner can only select between their specialities

    description = fields.Text(
        help="Context of the impression: Why/how the assessment was performed",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # FHIR: description

    encounter_id = fields.Many2one(
        "pod.encounter", required=True, readonly=True
    )
    # FHIR: encounter

    patient_id = fields.Many2one(
        related="encounter_id.patient_id", readonly=True, states={}
    )
    # FHIR: patient

    validation_date = fields.Datetime(readonly=True)
    # FHIR: date

    validation_user_id = fields.Many2one(
        "res.users", string="Validated by", readonly=True, copy=False
    )

    cancellation_date = fields.Datetime(readonly=True)

    cancellation_user_id = fields.Many2one(
        "res.users", string="Cancelled by", readonly=True, copy=False
    )
    finding_ids = fields.Many2many(
        comodel_name="pod.clinical.finding",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # FHIR: finding
    allergy_substance_ids = fields.Many2many(
        comodel_name="pod.allergy.substance",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    condition_ids = fields.One2many(
        comodel_name="pod.condition",
        string="Conditions",
        related="patient_id.pod_condition_ids",
    )

    condition_count = fields.Integer(
        related="patient_id.pod_condition_count"
    )

    summary = fields.Text(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    # FHIR: summary
    note = fields.Text(readonly=True, states={"draft": [("readonly", False)]})
    # FHIR: Note

    current_encounter = fields.Boolean(
        help="This field is only used to stand out the impressions "
        "of the current encounter in the tree view",
        compute="_compute_current_encounter",
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("pod.clinical.impression")
            or "/"
        )

    @api.depends("encounter_id")
    def _compute_current_encounter(self):
        for rec in self:
            current_encounter = False
            if self.env.context.get("encounter_id"):
                default_encounter = self.env.context.get("encounter_id")
                if default_encounter == rec.encounter_id.id:
                    current_encounter = True
            rec.current_encounter = current_encounter

    def _create_conditions_from_findings(self):
        finding_ids = self.finding_ids.filtered(
            lambda f: f.create_condition_from_clinical_impression
        )
        if finding_ids:
            for finding in finding_ids:
                condition = self.patient_id.pod_condition_ids.filtered(
                    lambda r: r.clinical_finding_id.id == finding.id
                )
                if not condition:
                    self.env["pod.condition"].create(
                        {
                            "patient_id": self.patient_id.id,
                            "clinical_finding_id": finding.id,
                            "origin_clinical_impression_id": self.id,
                        }
                    )

    def _create_allergies_from_findings(self):
        if self.allergy_substance_ids:
            for substance in self.allergy_substance_ids:
                allergy = self.patient_id.pod_allergy_ids.filtered(
                    lambda r: r.allergy_id.id == substance.id
                )
                if not allergy:
                    self.env["pod.condition"].create(
                        {
                            "patient_id": self.patient_id.id,
                            "is_allergy": True,
                            "allergy_id": substance.id,
                            "origin_clinical_impression_id": self.id,
                        }
                    )

    def _validate_clinical_impression_fields(self):
        return {
            "fhir_state": "completed",
            "validation_date": fields.Datetime.now(),
            "validation_user_id": self.env.user.id,
        }

    def validate_clinical_impression(self):
        self.ensure_one()
        self.write(self._validate_clinical_impression_fields())
        self._create_conditions_from_findings()
        self._create_allergies_from_findings()

    def _cancel_clinical_impression_fields(self):
        return {
            "fhir_state": "cancelled",
            "cancellation_date": fields.Datetime.now(),
            "cancellation_user_id": self.env.user.id,
        }

    def _cancel_related_conditions(self):
        related_conditions = self.condition_ids.filtered(
            lambda r: r.origin_clinical_impression_id.id == self.id
        )
        related_conditions.active = False

    def cancel_clinical_impression(self):
        self.ensure_one()
        self._cancel_related_conditions()
        self.write(self._cancel_clinical_impression_fields())
