from odoo import models


class ResPartnerAutomaticMerge(models.TransientModel):
    _inherit = "base.partner.merge.automatic.wizard"

    def action_merge(self):
        """Inject context for avoiding the duplicate reference constraint that
        happens when merging one contact with reference in another without
        reference.
        """
        return super(
            ResPartnerAutomaticMerge,
            self.with_context(partner_ref_unique_merging=True),
        ).action_merge()
