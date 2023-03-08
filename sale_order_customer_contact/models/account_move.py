from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    _FIELD_STATES = {"draft": [("readonly", False)], "open": [("readonly", False)]}

    customer_contact_id = fields.Many2one(
        "res.partner", "Contact", states=_FIELD_STATES
    )

    @api.onchange("partner_id")
    def onchange_partner(self):
        self.ensure_one()

        # Don't get a contact if there is no partner
        if not self.partner_id:
            return False

        # Contact is already set
        if self.customer_contact_id.parent_id == self.partner_id:
            return False

        self.customer_contact_id = self.partner_id.search(
            [
                ("commercial_partner_id", "=", self.partner_id.id),
                ("type", "=", "contact"),
                ("is_company", "=", False),
            ],
            limit=1,
        )

    @api.onchange("partner_id")
    @api.depends("customer_contact_id")
    def onchange_partner_domain_change(self):
        self.ensure_one()

        # Get the contact domain of there is a partner selected
        if not self.partner_id:
            return False

        res = dict()

        contacts = self.env["res.partner"].search(
            [
                ("commercial_partner_id", "=", self.partner_id.id),
                ("type", "=", "contact"),
                ("is_company", "=", False),
            ]
        )

        if contacts:
            domain = [("id", "in", contacts.ids)]
            res["domain"] = {"customer_contact_id": domain}

        return res
