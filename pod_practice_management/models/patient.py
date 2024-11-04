from odoo import models, fields, _, api, Command
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.addons.phone_validation.tools import phone_validation
import logging

_logger = logging.getLogger(__name__)

external_tracking_fields = {
    "last_consultation_date",
    "active_status",
    "active_date",
}

internal_tracking_fields = {
    "practice_info_notes",
    "age",
    "date_of_birth",
}


class Patient(models.Model):
    _name = "podiatry.patient"
    _description = "Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "last_name, first_name"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contact",
        ondelete="restrict",
        compute_sudo=True,
    )
    first_name = fields.Char(required=True, tracking=True)
    last_name = fields.Char(required=True, tracking=True)
    name = fields.Char(related="partner_id.name")
    phone = fields.Char(related="partner_id.phone", readonly=False)
    mobile = fields.Char(related="partner_id.mobile", readonly=False)
    street = fields.Char(related="partner_id.street", readonly=False)
    street2 = fields.Char(related="partner_id.street2", readonly=False)
    city = fields.Char(related="partner_id.city", readonly=False)
    state_id = fields.Many2one(related="partner_id.state_id", readonly=False)
    country_id = fields.Many2one(related="partner_id.country_id", readonly=False)
    zip = fields.Char(related="partner_id.zip", readonly=False)
    email = fields.Char(related="partner_id.email", readonly=False)
    date_of_birth = fields.Date(tracking=True)
    age = fields.Integer(compute="_compute_age", store=True)
    allergies = fields.Text()
    active_pathology_count = fields.Integer(compute="_compute_active_pathology_count")
    contact_ids = fields.One2many(
        comodel_name="podiatry.patient.contact",
        inverse_name="patient_id",
        string="Patient Contacts",
        groups="pod_practice_management.group_podiatry_practice_user",
    )
    practice_info_notes = fields.Html(
        string="Notes",
        tracking=True,
    )
    practice_ids = fields.Many2many(
        comodel_name="podiatry.practice",
        relation="podiatry_practice_patient_rel",
        column1="patient_id",
        column2="practice_id",
        string="Practices",
    )
    active_status = fields.Selection(
        selection=[("yes", "Yes"), ("no", "No")],
        required=True,
        default="yes",
        tracking=True,
    )
    pathology_ids = fields.One2many(
        comodel_name="podiatry.patient.pathology",
        inverse_name="patient_id",
        string="Pathologies",
    )
    active_date = fields.Date(tracking=True, help="When the patient was activated")
    inactive_since = fields.Date(compute="_compute_is_active", store=True)
    is_active = fields.Boolean(
        compute="_compute_is_active", store=True, tracking=True, default=True
    )
    stage = fields.Selection(
        selection=[("inactive", "Not Active"), ("active", "Active")],
        compute="_compute_stage",
        store=True,
    )
    last_consultation_date = fields.Date(tracking=True)

    @api.depends("pathology_ids.stage")
    def _compute_active_pathology_count(self):
        for rec in self:
            rec.active_pathology_count = len(
                rec.pathology_ids.filtered(lambda r: r.stage == "active")
            )

    @api.depends("is_active")
    def _compute_stage(self):
        for rec in self:
            rec.stage = "active" if rec.is_active else "inactive"

    @api.depends("pathology_ids.stage")
    def _compute_is_active(self):
        for rec in self:
            unresolved_pathologies = rec.pathology_ids.filtered(
                lambda p: p.stage != "resolved"
            )
            rec.is_active = rec.active_status == "yes"
            rec.inactive_since = (
                unresolved_pathologies[0].pathology_date
                if unresolved_pathologies
                else False
            )

    @api.depends("date_of_birth")
    def _compute_age(self):
        for rec in self:
            rec.age = (
                relativedelta(date.today(), rec.date_of_birth).years
                if rec.date_of_birth
                else 0
            )

    def action_view_patient_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "podiatry.patient",
            "res_id": self.id,
            "context": self._context,
        }

    def action_consulted_today(self):
        self.ensure_one()
        self.last_consultation_date = date.today()
        return {
            "view_mode": "form",
            "res_model": "podiatry.patient",
            "res_id": self.id,
        }

    def _track_subtype(self, init_values):
        return self.env.ref("mail.mt_note")

    def _track_template(self, changes):
        res = super()._track_template(changes)
        params = set(changes)
        external = bool(external_tracking_fields & params)
        if external:
            first_external_field = (external_tracking_fields & params).pop()
            res[first_external_field] = (
                self.env.ref(
                    "pod_practice_management.mail_template_patient_status_update"
                ),
                {
                    # "auto_delete_message": False,
                    "subtype_id": self.env.ref(
                        "pod_practice_management.subtype_patient_external_update"
                    ).id,
                    "email_layout_xmlid": "mail.mail_notification_light",
                },
            )
        if "practice_info_notes" in changes:
            res["practice_info_notes"] = (
                self.env.ref(
                    "pod_practice_management.mail_template_patient_new_internal_note"
                ),
                {
                    # "auto_delete_message": False,
                    "subtype_id": self.env.ref(
                        "pod_practice_management.subtype_patient_internal_update"
                    ).id,
                    "email_layout_xmlid": "mail.mail_notification_light",
                },
            )
        return res

    def recompute_followers(self):
        for patient in self:
            current_followers = patient.message_partner_ids
            future_followers = patient.practice_ids.mapped("staff_ids.partner_id")
            removed_followers = current_followers - future_followers
            if removed_followers:
                patient.message_unsubscribe(removed_followers.ids)
                patient.pathology_ids.message_unsubscribe(removed_followers.ids)
            if future_followers:
                patient.message_subscribe(future_followers.ids)
                patient.pathology_ids.message_subscribe(future_followers.ids)
