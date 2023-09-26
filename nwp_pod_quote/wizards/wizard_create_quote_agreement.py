

from odoo import api, fields, models


class WizardCreateQuoteAgreement(models.TransientModel):

    _name = "wizard.create.quote.agreement"
    _description = "wizard.create.quote.agreement"

    agreement_id = fields.Many2one("pod.coverage.agreement")

    possible_template_ids = fields.Many2many("pod.coverage.template")
    coverage_template_id = fields.Many2one(
        "pod.coverage.template",
        required=True,
        domain="[('id', 'in', possible_template_ids)]",
    )

    possible_practice_ids = fields.Many2many("res.partner")
    practice_id = fields.Many2one(
        "res.partner",
        required=True,
        domain="[('id', 'in', possible_practice_ids)]",
    )

    @api.model
    def default_get(self, fields_list):
        rec = super().default_get(fields_list)
        agreement_id = self.env.context.get("active_id", False)
        rec["agreement_id"] = agreement_id
        agreement = self.env["pod.coverage.agreement"].browse(agreement_id)
        rec["possible_practice_ids"] = [(6, 0, agreement.practice_ids.ids)]
        rec["possible_template_ids"] = [(6, 0, agreement.coverage_template_ids.ids)]
        return rec

    def generate_quote(self):
        self.ensure_one()
        quote = self.env["pod.quote"].create(
            {
                "practice_id": self.practice_id.id,
                "coverage_template_id": self.coverage_template_id.id,
                "payor_id": self.coverage_template_id.payor_id.id,
                "origin_agreement_id": self.agreement_id.id,
            }
        )
        for item in self.agreement_id.item_ids:
            quote.add_agreement_line_id = item
            quote.button_add_line()

        result = self.env["ir.actions.act_window"]._for_xml_id(
            "nwp_pod_quote.action_quotes"
        )
        result["views"] = [(False, "form")]
        result["res_id"] = quote.id
        return result
