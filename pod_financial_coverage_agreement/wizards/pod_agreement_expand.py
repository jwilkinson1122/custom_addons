from datetime import timedelta

from odoo import fields, models


class PodiatryAgreementExpand(models.TransientModel):

    _name = "pod.agreement.expand"
    _description = "TODO"

    agreement_id = fields.Many2one("pod.coverage.agreement", required=True)
    name = fields.Char(required=True)
    difference = fields.Float(
        string="Indicate the percentage to apply to the agreement"
    )
    date_to = fields.Date(required=True)

    def _get_copy_vals(self):
        return {
            "parent_id": self.agreement_id.id,
            "name": self.name,
            "date_from": self.agreement_id.date_to + timedelta(days=1),
            "date_to": self.date_to,
            "coverage_template_ids": [
                (6, 0, self.agreement_id.coverage_template_ids.ids)
            ],
        }

    def _expand(self):
        self.ensure_one()
        new_agreement = self.agreement_id.copy(self._get_copy_vals())
        self.env["pod.agreement.change.prices"].create(
            {"difference": self.difference}
        ).with_context(
            active_ids=new_agreement.ids,
            active_model=new_agreement._name,
            active_id=new_agreement.id,
        ).change_prices()
        return new_agreement

    def expand(self):
        return self._expand().get_formview_action()