

from odoo import _, fields, models


class PodiatryAgreementChangePrices(models.TransientModel):
    _name = "pod.agreement.change.prices"
    _description = "pod.agreement.change.prices"

    difference = fields.Float(
        string="Indicate the percentage to apply to the agreement"
    )

    def change_prices(self):
        context = dict(self._context or {})
        agreements = self.env["pod.coverage.agreement"].browse(
            context.get("active_ids")
        )
        for agreement in agreements:
            for item in agreement.item_ids:
                item.total_price = item.total_price + (
                    (item.total_price * self.difference) / 100
                )
            agreement.message_post(
                body=_("Prices have been changed by a %s &#037 by %s")
                % (self.difference, self.env.user.display_name)
            )
