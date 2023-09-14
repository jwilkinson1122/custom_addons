

from odoo import api, fields, models


class PodiatryRequest(models.AbstractModel):
    _inherit = "pod.request"

    procedure_request_id = fields.Many2one(
        string="Parent Procedure Request",
        comodel_name="pod.procedure.request",
        ondelete="restrict",
        index=True,
    )  # FHIR Field: BasedOn
    procedure_request_ids = fields.One2many(
        string="Associated Procedure Requests",
        comodel_name="pod.procedure.request",
        compute="_compute_procedure_request_ids",
    )
    procedure_request_count = fields.Integer(
        compute="_compute_procedure_request_ids",
        string="# of Procedure Requests",
        copy=False,
        default=0,
    )

    def _compute_procedure_request_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            procedure_requests = self.env["pod.procedure.request"].search(
                [(inverse_field_name, "=", rec.id)]
            )
            rec.procedure_request_ids = [(6, 0, procedure_requests.ids)]
            rec.procedure_request_count = len(rec.procedure_request_ids)

    @api.model
    def _get_request_models(self):
        res = super(PodiatryRequest, self)._get_request_models()
        res.append("pod.procedure.request")
        return res

    @api.constrains("procedure_request_id")
    def _check_hierarchy_procedure_request(self):
        for record in self:
            record._check_hierarchy_children({})

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.procedure_request_id)
        return res
