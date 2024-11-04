from odoo import models, fields, api, _
from datetime import date, datetime
import pytz
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PatientPathology(models.Model):
    _name = "podiatry.patient.pathology"
    _description = "Patient Pathology"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "diagnosis"

    @api.model
    def _today(self):
        """Get the current date in the user's time zone."""
        return datetime.now(pytz.timezone(self.env.user.tz or "GMT"))

    patient_id = fields.Many2one(
        comodel_name="podiatry.patient",
        string="Patient",
        readonly=True,
        required=True,
        ondelete="cascade",
    )
    patient_name = fields.Char(related="patient_id.name")
    diagnosis = fields.Char(tracking=True)
    pathology_date = fields.Date(string="Date of Pathology", default=_today)
    pathology_date_na = fields.Boolean(string="N/A", default=False)
    internal_notes = fields.Html(tracking=True)
    external_notes = fields.Html(tracking=True)
    treatment_professional_ids = fields.Many2many(
        comodel_name="res.users",
        relation="patient_pathology_treatment_pro_rel",
        column1="patient_pathology_id",
        column2="treatment_pro_id",
        string="Treatment Professionals",
        domain=[("is_treatment_professional", "=", True)],
        tracking=True,
    )
    resolution_date = fields.Date(
        tracking=True, help="The date when the pathology was actually resolved."
    )
    stage = fields.Selection(
        selection=[("active", "Active"), ("resolved", "Resolved")],
        compute="_compute_stage",
        store=True,
    )

    @api.constrains("pathology_date_na", "pathology_date")
    def _constrain_date_na(self):
        for rec in self:
            if not rec.pathology_date_na and not rec.pathology_date:
                raise ValidationError(
                    _("If pathology date is not set, the N/A box must be checked.")
                )

    @api.onchange("pathology_date_na")
    def _onchange_pathology_date_na(self):
        if self.pathology_date_na:
            self.pathology_date = None

    @api.onchange("pathology_date")
    def _onchange_pathology_date(self):
        if self.pathology_date:
            self.pathology_date_na = False

    @api.depends("resolution_date")
    def _compute_stage(self):
        for rec in self:
            rec.stage = (
                "resolved"
                if rec.resolution_date and rec.resolution_date <= date.today()
                else "active"
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec.message_subscribe(rec.patient_id.message_partner_ids)
            rec.patient_id.message_post(
                body=_("A new pathology was created: %s" % rec.diagnosis)
            )
        return records

    def unlink(self):
        for rec in self:
            rec.patient_id.message_post(
                body=_("A pathology was deleted: %s" % rec.diagnosis)
            )
        return super().unlink()

    def action_view_pathology_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "podiatry.patient.pathology",
            "res_id": self.id,
            "context": self._context,
        }
