from odoo import fields, models


class PodiatryCoverageAgreementTemplate(models.TransientModel):
    _name = "pod.coverage.agreement.template"
    _description = "pod.coverage.agreement.template"

    agreement_id = fields.Many2one(
        "pod.coverage.agreement", readonly=True, required=True
    )
    template_id = fields.Many2one(
        "pod.coverage.agreement", domain=[("is_template", "=", True)]
    )
    set_items = fields.Boolean(default=False)

    def run(self):
        self.ensure_one()
        self.agreement_id.set_template(self.template_id, self.set_items)
