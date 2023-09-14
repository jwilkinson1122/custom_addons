

from odoo import api, fields, models


class PodiatryRequest(models.AbstractModel):
    _inherit = "pod.request"

    careplan_id = fields.Many2one(
        string="Parent Careplan",
        comodel_name="pod.careplan",
        ondelete="restrict",
        index=True,
    )  # FHIR Field: BasedOn
    careplan_ids = fields.One2many(
        string="Associated Care Plans",
        comodel_name="pod.careplan",
        compute="_compute_careplan_ids",
    )
    careplan_count = fields.Integer(
        compute="_compute_careplan_ids",
        string="# of Care Plans",
        copy=False,
        default=0,
    )

    def _compute_careplan_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            careplans = self.env["pod.careplan"].search(
                [(inverse_field_name, "=", rec.id)]
            )
            rec.careplan_ids = [(6, 0, careplans.ids)]
            rec.careplan_count = len(rec.careplan_ids)

    @api.model
    def _get_request_models(self):
        res = super(PodiatryRequest, self)._get_request_models()
        res.append("pod.careplan")
        return res

    @api.constrains("careplan_id")
    def _check_hierarchy_careplan(self):
        for record in self:
            record._check_hierarchy_children({})

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.careplan_id)
        return res
