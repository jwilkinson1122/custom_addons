from odoo import api, fields, models


class PodiatryRequestGroupDiscount(models.TransientModel):
    _name = "pod.request.group.discount"
    _description = "Add discount on a request group"

    request_group_id = fields.Many2one(
        "pod.request.group", required=True, readonly=True
    )
    discount = fields.Float(required=True, digits="Discount")
    pod_sale_discount_id = fields.Many2one("pod.sale.discount", required=True)
    percentage = fields.Float(
        related="pod_sale_discount_id.percentage", readonly=True
    )
    is_fixed = fields.Boolean(
        related="pod_sale_discount_id.is_fixed", readonly=True
    )

    @api.onchange("pod_sale_discount_id")
    def _onchange_discount(self):
        self.discount = self.pod_sale_discount_id.percentage

    def get_discount_update_vals(self):
        return {
            "pod_sale_discount_id": self.pod_sale_discount_id.id,
            "discount": self.discount,
        }

    def _run_childs(self, request, models, vals):
        fieldname = request._get_parent_field_name()
        for model in models:
            childs = model.search(
                [
                    (fieldname, "=", request.id),
                    ("parent_id", "=", request.id),
                    ("parent_model", "=", request._name),
                    ("state", "!=", "cancelled"),
                ]
            )
            childs.write(vals)
            for child in childs:
                self._run_childs(child, models, vals)

    def run(self):
        self.ensure_one()
        vals = self.get_discount_update_vals()
        self.request_group_id.write(vals)
        models = [
            self.env[model] for model in self.request_group_id._get_request_models()
        ]
        self._run_childs(self.request_group_id, models, vals)
