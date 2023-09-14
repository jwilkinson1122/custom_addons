from datetime import datetime, timedelta

from odoo import api, fields, models


class PodiatryPatientCreateDiagnosticReport(models.TransientModel):

    _name = "pod.patient.create.diagnostic.report"
    _description = "Create a diagnostic report from patient"

    patient_id = fields.Many2one("pod.patient", readonly=True)
    encounter_id = fields.Many2one(
        "pod.encounter",
        required=True,
        compute="_compute_default_encounter",
    )
    template_id = fields.Many2one(
        "pod.diagnostic.report.template",
        required=True,
        domain="['|',('template_type','=','general'), '&', "
        "('create_uid','=',uid), ('template_type', '=', 'user')]",
    )
    lang = fields.Selection(
        string="Language",
        selection="_get_lang",
        required=True,
        default=lambda r: r.env.user.lang,
    )

    show_encounter_warning = fields.Boolean(default=False)
    encounter_warning = fields.Char(
        default="This encounter date is more than a week ago. Review it",
        readonly=True,
    )

    @api.onchange("encounter_id")
    def check_encounter_date(self):
        if (datetime.now() - self.encounter_id.create_date) >= timedelta(
            days=7
        ):
            self.show_encounter_warning = True

    @api.onchange("patient_id")
    def _compute_default_encounter(self):
        self.encounter_id = self.patient_id._get_last_encounter()

    @api.model
    def _get_lang(self):
        return self.env["res.lang"].get_installed()

    def _generate_kwargs(self):
        return {"encounter": self.encounter_id}

    def generate(self):
        self.ensure_one()
        report = self.template_id.with_context(
            lang=self.lang
        )._generate_report(**self._generate_kwargs())
        return report.get_formview_action()
