from odoo import models, fields, api, _
from datetime import datetime, date
import pytz
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

external_tracking_fields = {
    "pathology",
    "pathology_date",
    "external_notes",
}

internal_tracking_fields = {"internal_notes"}


class MedicalPathology(models.Model):
    _name = "medical.pathology"
    _description = "Medical Pathology"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "pathology"

    @api.model
    def _today(self):
        """Get the current date in the user's time zone."""
        return datetime.now(pytz.timezone(self.env.user.tz or "GMT"))

    patient_id = fields.Many2one(
        comodel_name="contact.patient",
        string="Patient",
        readonly=True,
        required=True,
        ondelete="cascade",
    )
    patient_name = fields.Char(related="patient_id.name")
    pathology = fields.Char(tracking=True)
    pathology_date = fields.Date(tracking=True, help="pathology date")
    pathology_date_na = fields.Boolean(string="N/A", default=False)
    internal_notes = fields.Html(tracking=True)
    external_notes = fields.Html(tracking=True)
    treatment_professional_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="patient_treatment_pro_rel",
        column1="patient_pathology_id",
        column2="treatment_pro_id",
        string="Treatment Professionals",
        domain=[("is_practitioner", "=", True)],
        tracking=True,
    )

    stage = fields.Selection(
        selection=[("active", "Active"), ("resolved", "Resolved")],
        compute="_compute_stage",
    )

    @api.constrains("pathology_date_na", "pathology_date")
    def constrain_date_blank_only_if_na(self):
        for rec in self:
            if not rec.pathology_date_na and not rec.pathology_date:
                raise ValidationError(
                    _("If pathology date is not set, the N/A box must be checked.")
                )

    @api.onchange("pathology_date_na")
    def _onchange_pathology_date_na(self):
        for rec in self:
            if rec.pathology_date_na:
                rec.pathology_date = None

    @api.onchange("pathology_date")
    def _onchange_pathology_date(self):
        for rec in self:
            if rec.pathology_date:
                rec.pathology_date_na = False

    @api.depends("pathology_date")
    def _compute_stage(self):
        for rec in self:
            if rec.pathology_date and rec.pathology_date <= date.today():
                rec.stage = "resolved"
            else:
                rec.stage = "active"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res.sudo():
            rec.message_subscribe(rec.patient_id.message_partner_ids)
            msg_body = _("A new pathology was created for this patient.")
            if rec.pathology:
                msg_body += _(" Pathology: %s." % rec.pathology)
            rec.patient_id.message_post(body=msg_body, message_type="comment")
        return res

    def unlink(self):
        for rec in self:
            msg_body = _("A pathology was deleted.")
            if rec.pathology:
                msg_body += _(" Pathology: %s." % rec.pathology)
            rec.patient_id.message_post(body=msg_body, message_type="comment")
        return super().unlink()

    def action_view_pathology_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "medical.pathology",
            "res_id": self.id,
            "context": self._context,
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
                    "nwpl_odoo_master.mail_template_patient_pathology_status_update"
                ),
                {
                    "auto_delete_message": False,
                    "subtype_id": self.env.ref(
                        "nwpl_odoo_master.subtype_patient_pathology_external_update"
                    ).id,
                    "email_layout_xmlid": "mail.mail_notification_light",
                },
            )
        if "internal_notes" in changes:
            res["internal_notes"] = (
                self.env.ref(
                    "nwpl_odoo_master.mail_template_patient_pathology_new_internal_note"
                ),
                {
                    "auto_delete_message": False,
                    "subtype_id": self.env.ref(
                        "nwpl_odoo_master.subtype_patient_pathology_internal_update"
                    ).id,
                    "email_layout_xmlid": "mail.mail_notification_light",
                },
            )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.patient_id.recompute_followers()
        return res
