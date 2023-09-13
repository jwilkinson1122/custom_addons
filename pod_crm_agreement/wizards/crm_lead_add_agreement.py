from odoo import _, fields, models


class CrmLeadAddAgreement(models.TransientModel):
    _name = "crm.lead.add.agreement"
    _description = "crm.lead.add.agreement"

    lead_id = fields.Many2one("crm.lead", required=True)
    coverage_template_ids = fields.One2many(
        comodel_name="pod.coverage.template",
        related="lead_id.partner_id.commercial_partner_id" ".coverage_template_ids",
        readonly=True,
    )
    agreement_id = fields.Many2one("pod.coverage.agreement", required=True)
    agreement_ids = fields.Many2many(
        "pod.coverage.agreement",
        related="lead_id.agreement_ids",
        string="Current agreement ids",
    )

    def link_to_existing(self):
        self.ensure_one()
        self.lead_id.write({"agreement_ids": [(4, self.agreement_id.id)]})
        return {}

    def generate_new(self):
        self.ensure_one()
        vals = self.agreement_id.copy_data()[0]
        vals["date_from"] = fields.Date.today()
        vals["name"] += _(" (Copy)")
        vals.pop("date_to", False)
        new_agreement = self.env["pod.coverage.agreement"].create(vals)
        self.lead_id.write({"agreement_ids": [(4, new_agreement.id)]})
        return {}
