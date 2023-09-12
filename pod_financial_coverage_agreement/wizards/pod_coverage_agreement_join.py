from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PodiatryCoverageAgreementJoin(models.TransientModel):
    _name = "pod.coverage.agreement.join"
    _description = "pod.coverage.agreement.join"

    def _default_agreements(self):
        context = self.env.context
        return self.env[context.get("active_model")].browse(context.get("active_ids"))

    agreement_ids = fields.Many2many(
        "pod.coverage.agreement", default=_default_agreements
    )

    def check_possible_join(self):
        company = self.agreement_ids.mapped("company_id")
        if len(company) > 1:
            raise ValidationError(_("The company must be the same"))
        coverages = self.agreement_ids.mapped("coverage_template_ids")
        centers = self.agreement_ids.mapped("center_ids")
        for agreement in self.agreement_ids:
            if coverages != agreement.coverage_template_ids:
                raise ValidationError(_("The templates must be the same"))
            if centers != agreement.center_ids:
                raise ValidationError(_("The centers must be the same"))

    def run(self):
        if len(self.agreement_ids) < 2:
            raise ValidationError(_("You must select multiple agreements"))
        self.check_possible_join()
        final_agreement = self.agreement_ids[0]
        for agreement in self.agreement_ids[1:]:
            agreement.item_ids.write({"coverage_agreement_id": final_agreement.id})
            if agreement.active:
                agreement.toggle_active()
            agreement.message_post(
                body=_("Joined to agreement %s") % (final_agreement.display_name)
            )
            final_agreement.message_post(
                body=_("Joined items from agreement %s") % (agreement.display_name)
            )
        return
