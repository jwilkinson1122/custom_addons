from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PodiatryRequest(models.AbstractModel):
    _inherit = "pod.request"

    document_reference_ids = fields.One2many(
        string="Associated Documents",
        comodel_name="pod.document.reference",
        compute="_compute_document_reference_ids",
    )
    document_reference_count = fields.Integer(
        compute="_compute_document_reference_ids",
        string="# of Document References",
        copy=False,
        default=0,
    )
    document_reference_id = fields.Many2one(
        "pod.document.reference", required=False, readonly=True, index=True
    )  # the field must be created, but it should allways be null

    @api.constrains("document_reference_id")
    def check_document_reference(self):
        if self.filtered(lambda r: r.document_reference_id):
            raise ValidationError(
                _("Document reference cannot be parent of other documents.")
            )

    @api.model
    def _get_request_models(self):
        res = super(PodiatryRequest, self)._get_request_models()
        res.append("pod.document.reference")
        return res

    def _compute_document_reference_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            documents = self.env["pod.document.reference"].search(
                [(inverse_field_name, "=", rec.id)]
            )
            rec.document_reference_ids = [(6, 0, documents.ids)]
            rec.document_reference_count = len(rec.document_reference_ids)

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.document_reference_id)
        return res
