

from odoo import api, fields, models


class PodiatryRequest(models.AbstractModel):
    _inherit = "pod.request"

    laboratory_request_ids = fields.One2many(
        string="Laboratory requests",
        comodel_name="pod.laboratory.request",
        compute="_compute_laboratory_request_ids",
    )
    laboratory_request_count = fields.Integer(
        compute="_compute_laboratory_request_ids",
        string="# of Laboratory requests",
        copy=False,
        default=0,
    )
    laboratory_request_id = fields.Many2one(
        "pod.laboratory.request", required=False, readonly=True
    )

    @api.model
    def _get_request_models(self):
        res = super(PodiatryRequest, self)._get_request_models()
        res.append("pod.laboratory.request")
        return res

    def _compute_laboratory_request_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            requests = self.env["pod.laboratory.request"].search(
                [(inverse_field_name, "=", rec.id)]
            )
            rec.laboratory_request_ids = [(6, 0, requests.ids)]
            rec.laboratory_request_count = len(rec.laboratory_request_ids)

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.laboratory_request_id)
        return res
