from odoo import _, fields, models
from odoo.exceptions import UserError


class PodiatryDocumentTemplate(models.Model):
    # FHIR Entity: Document Refernece
    # (https://www.hl7.org/fhir/documentreference.html)
    _name = "pod.document.template"
    _description = "Podiatry Document Template"
    _order = "sequence desc"

    document_type_id = fields.Many2one(
        "pod.document.type",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    document_type = fields.Selection(
        related="document_type_id.document_type",
        readonly=True,
        string="Document type reference",
    )
    sequence = fields.Integer()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("current", "Current"),
            ("superseded", "Su" "perseded"),
        ],
        required=True,
        default="draft",
        readonly=True,
    )
    lang_ids = fields.One2many(
        "pod.document.template.lang", inverse_name="document_template_id"
    )

    def unpost(self):
        self.state = "superseded"

    def render_template(self, model, res_id, post_process=False):
        if self.document_type == "action":
            if not self.lang_ids:
                raise UserError(_("No documents can be found"))
            lang = self.env.context.get("render_language", self.env.lang)
            lang_id = self.lang_ids.filtered(lambda r: r.lang == lang)
            if not lang_id:
                lang = self.env.lang
                lang_id = self.lang_ids.filtered(lambda r: r.lang == lang)
            if not lang_id:
                lang_id = self.lang_ids[0]
            return self.env["mail.template"]._render_template(
                lang_id.text, model, [res_id], post_process=post_process
            )[res_id]
        raise UserError(_("Function must be defined"))


class PodiatryDocumentTemplateLang(models.Model):
    _name = "pod.document.template.lang"
    _description = "Podiatry Document Template Lang"
    _inherit = "pod.document.language"
    _rec_name = "lang"

    document_template_id = fields.Many2one("pod.document.template", required=True)
    text = fields.Html(sanitize=True)

    _sql_constraints = [
        (
            "unique_language",
            "UNIQUE(lang, document_template_id)",
            "The language is allowed only once on a template.",
        )
    ]
