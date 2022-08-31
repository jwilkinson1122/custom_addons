

from odoo import api, fields, models


class PodiatryRequest(models.AbstractModel):
    _inherit = "podiatry.request"

    request_group_id = fields.Many2one(
        string="Parent Request group",
        comodel_name="podiatry.request.group",
        ondelete="restrict",
        index=True,
    )  # Field: BasedOn

    request_group_ids = fields.One2many(
        string="Parent Request Group",
        comodel_name="podiatry.request.group",
        compute="_compute_request_group_ids",
    )
    request_group_count = fields.Integer(
        compute="_compute_request_group_ids",
        string="# of Request Groups",
        copy=False,
        default=0,
    )

    def _compute_request_group_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            request_groups = self.env["podiatry.request.group"].search(
                [(inverse_field_name, "=", rec.id)]
            )
            rec.request_group_ids = [(6, 0, request_groups.ids)]
            rec.request_group_count = len(rec.request_group_ids)

    @api.model
    def _get_request_models(self):
        res = super(PodiatryRequest, self)._get_request_models()
        res.append("podiatry.request.group")
        return res

    @api.constrains("request_group_id")
    def _check_hierarchy_request_group(self):
        for record in self:
            record._check_hierarchy_children({})

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.request_group_id)
        return res
