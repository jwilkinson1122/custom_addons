from odoo import fields, models


class ResPartner(models.Model):
    """Add relation affiliate_ids."""

    _inherit = "res.partner"

    # force "active_test" domain to bypass _search() override
    child_ids = fields.One2many(
        domain=[("active", "=", True), ("is_company", "=", False)]
    )

    # force "active_test" domain to bypass _search() override
    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[("active", "=", True), ("is_company", "=", True)],
    )
