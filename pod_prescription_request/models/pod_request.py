
from odoo import api, fields, models


class PodRequest(models.AbstractModel):
    _inherit = "pod.request"

    prescription_request_id = fields.Many2one(
        string="Parent prescription request",
        comodel_name="pod.prescription.request",
        ondelete="restrict",
        index=True,
    )  # FHIR Field: BasedOn
    prescription_request_ids = fields.One2many(
        string="Prescription requests",
        comodel_name="pod.prescription.request",
        compute="_compute_prescription_request_ids",
    )
    prescription_request_count = fields.Integer(
        compute="_compute_prescription_request_ids",
        string="# of Prescription Rx Request",
        copy=False,
        default=0,
    )

    # prescription_line_ids = fields.One2many('pod.rx.order.line', 'name', 'Rx Order Line')

    def _compute_prescription_request_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            prescription_requests = self.env[
                "pod.prescription.request"
            ].search([(inverse_field_name, "=", rec.id)])
            rec.prescription_request_ids = [(6, 0, prescription_requests.ids)]
            rec.prescription_request_count = len(rec.prescription_request_ids)

    @api.model
    def _get_request_models(self):
        res = super(PodRequest, self)._get_request_models()
        res.append("pod.prescription.request")
        return res

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.prescription_request_id)
        return res

    @api.constrains("prescription_request_id")
    def _check_hierarchy_prescription_request(self):
        for record in self:
            record._check_hierarchy_children({})
