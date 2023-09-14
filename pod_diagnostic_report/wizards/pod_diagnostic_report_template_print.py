# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PodiatryDiagnosticReportTemplatePrint(models.TransientModel):
    _name = "pod.diagnostic.report.template.print"
    _description = (
        "This wizard allows to print from template with the selected language"
    )
    diagnostic_template_id = fields.Many2one(
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

    def print(self):
        return (
            self.env["ir.actions.report"]
            ._for_xml_id(
                "pod_diagnostic_report.pod_diagnostic_report_template_preview"
            )
            .with_context(lang=self.lang, force_lang=self.lang)
            .report_action(
                self.diagnostic_template_id,
                data=dict(dummy=True),
                config=False,
            )
        )
