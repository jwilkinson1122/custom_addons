from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

INVOICE = "invoice"


class ResPartner(models.Model):
    """Add relation affiliate_ids."""

    _inherit = "res.partner"

    use_parent_invoice_address = fields.Boolean()

    highest_parent_id = fields.Many2one(
        "res.partner",
        compute="_get_highest_parent_id",
        store="True",
        string="Highest parent",
    )

    is_company_parent = fields.Boolean(
        compute="_get_is_company_parent",
        store="True",
        string="Is a Parent Company",
        help="A parent company is a “Company” type contact for which at least "
        "one “Affiliate” is defined and for which no related"
        " company is defined",
    )

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

    @api.depends("company_type", "affiliate_ids", "parent_id")
    def _get_is_company_parent(self):
        """compute if contact is a parent company or not"""
        for rec in self:
            is_company_parent = False
            if (
                rec.company_type == "company"
                and rec.affiliate_ids
                and not rec.parent_id
            ):
                is_company_parent = True
            rec.is_company_parent = is_company_parent

    def compute_partner_parent_ids(self, rec=False, res=[]):
        if rec.parent_id:
            res.append(rec.parent_id.id)
            self.compute_partner_parent_ids(rec=rec.parent_id, res=res)
        return res

    @api.depends("parent_id", "child_ids")
    def _get_highest_parent_id(self):
        for rec in self:
            if rec.parent_id:
                res = rec.compute_partner_parent_ids(rec=rec)
                if res:
                    rec.highest_parent_id = res[-1]

    @api.model
    def compute_all_top_parent_id(self):
        partner_ids = self.search(
            [("is_company_parent", "=", False), ("parent_id", "!=", False)]
        )
        for partner in partner_ids:
            res = partner.compute_partner_parent_ids(rec=partner)
            if res:
                partner.highest_parent_id = res[-1]

    def write(self, vals):
        super().write(vals)
        if "parent_id" in vals:
            for record in self:
                record.compute_all_top_parent_id()
        return True

    def address_get(self, adr_pref=None):
        res = super().address_get(adr_pref)

        commercial_partner = self.commercial_partner_id

        use_parent_invoice_address = (
            commercial_partner.use_parent_invoice_address
            and commercial_partner.parent_id
        )

        if INVOICE in res and use_parent_invoice_address:
            res[INVOICE] = self.parent_id.address_get([INVOICE])[INVOICE]

        return res

    @api.onchange("parent_id")
    def _update_use_parent_invoice_address(self):
        if not self.parent_id:
            self.use_parent_invoice_address = False

    def open_affiliate_form(self):
        """Open affiliate contact form from the parent partner form view"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }
