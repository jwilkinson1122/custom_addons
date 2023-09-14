from odoo import api, fields, models


class PodiatryDocumentReferenceChangeLanguage(models.TransientModel):
    _name = "pod.document.reference.change.language"
    _description = "pod document reference change language"

    document_reference_id = fields.Many2one(
        "pod.document.reference", required=True, readonly=True
    )
    document_type_id = fields.Many2one(
        "pod.document.type",
        related="document_reference_id.document_type_id",
        readonly=True,
    )
    lang_ids = fields.Many2many("res.lang", compute="_compute_lang_ids")
    lang_id = fields.Many2one(
        "res.lang",
        "Language",
        required=True,
        domain="[('id', 'in', lang_ids)]",
    )

    @api.depends("document_reference_id")
    def _compute_lang_ids(self):
        for res in self:
            langs = res.document_reference_id.document_template_id.lang_ids
            if res.document_reference_id.lang:
                langs = langs.filtered(
                    lambda r: r.lang != res.document_reference_id.lang
                )
            res.lang_ids = self.env["res.lang"].search(
                [("code", "in", langs.mapped("lang"))]
            )

    def run(self):
        self.ensure_one()
        return self.document_reference_id.change_lang(self.lang_id.code)
