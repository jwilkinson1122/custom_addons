

from odoo import api, fields, models


class PodiatryRequest(models.AbstractModel):
    _inherit = "podiatry.request"

    device_request_id = fields.Many2one(
        string="Parent device request",
        comodel_name="podiatry.device.request",
        ondelete="restrict",
        index=True,
    )  # Field: BasedOn
    device_request_ids = fields.One2many(
        string="Prescription Requests",
        comodel_name="podiatry.device.request",
        compute="_compute_device_request_ids",
    )
    device_request_count = fields.Integer(
        compute="_compute_device_request_ids",
        string="# of Device Requests",
        copy=False,
        default=0,
    )

    def _compute_device_request_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            device_requests = self.env[
                "podiatry.device.request"
            ].search([(inverse_field_name, "=", rec.id)])
            rec.device_request_ids = [(6, 0, device_requests.ids)]
            rec.device_request_count = len(rec.device_request_ids)

    @api.model
    def _get_request_models(self):
        res = super(PodiatryRequest, self)._get_request_models()
        res.append("podiatry.device.request")
        return res

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.device_request_id)
        return res

    @api.constrains("device_request_id")
    def _check_hierarchy_device_request(self):
        for record in self:
            record._check_hierarchy_children({})
