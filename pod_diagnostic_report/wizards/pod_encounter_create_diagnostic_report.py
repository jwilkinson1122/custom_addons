

from odoo import api, fields, models


class PodiatryEncounterCreateDiagnosticReport(models.TransientModel):

    _name = "pod.encounter.create.diagnostic.report"
    _description = "Generate report from encounter using a template"

    encounter_id = fields.Many2one("pod.encounter", required=True)
    template_id = fields.Many2one(
        "pod.diagnostic.report.template", required=True
    )
    lang = fields.Selection(
        string="Language",
        selection="_get_lang",
        required=True,
        default=lambda r: r.env.user.lang,
    )

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
