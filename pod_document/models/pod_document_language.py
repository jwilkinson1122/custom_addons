from odoo import api, fields, models


class PodiatryDocumentLanguage(models.AbstractModel):
    _name = "pod.document.language"
    _description = "Podiatry Document Language"

    @api.model
    def _get_languages(self):
        return self.env["res.lang"].get_installed()

    lang = fields.Selection(_get_languages, "Language", required=True)
