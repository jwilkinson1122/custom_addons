# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    """Extend sale.order to include branch-specific logic."""

    _inherit = "sale.order"

    branch_id = fields.Many2one(
        "res.branch",
        string="Branch",
        store=True,
        compute="_compute_branch",
        readonly=False,
        help="The branch associated with this sale order.",
    )

    affiliate_branch_ids = fields.Many2many(
        "res.branch",
        string="Affiliate Branches",
        compute="_compute_affiliate_branch_ids",
        store=True,
        help="Branches the current user is allowed to operate in.",
    )

    @api.depends("company_id")
    def _compute_affiliate_branch_ids(self):
        """Set allowed branches for the user."""
        for order in self:
            order.affiliate_branch_ids = self.env.user.branch_ids

    @api.depends("company_id")
    def _compute_branch(self):
        """Compute default branch based on user's allowed branches."""
        for order in self:
            order.branch_id = False
            user_branches = self.env.user.branch_ids
            if len(user_branches) == 1:
                # Set branch if only one branch is allowed
                branch = user_branches.filtered(
                    lambda b: b.company_id == order.company_id or not b.company_id
                )
                order.branch_id = branch[:1] if branch else False

    @api.constrains("branch_id", "partner_id")
    def _check_partner_branch_id(self):
        """Ensure the customer belongs to the same branch as the sale order."""
        for order in self:
            if (
                order.partner_id.branch_id
                and order.partner_id.branch_id != order.branch_id
            ):
                raise ValidationError(
                    _(
                        "The selected customer belongs to branch '%(partner_branch)s', "
                        "but this sale order is assigned to branch '%(order_branch)s'.\n"
                        "Please select a customer from the same branch.",
                        partner_branch=order.partner_id.branch_id.name,
                        order_branch=order.branch_id.name,
                    )
                )

    @api.constrains("branch_id", "order_line")
    def _check_order_line_branch_id(self):
        """Ensure that all products in the order line belong to the same branch."""
        for order in self:
            mismatched_products = order.order_line.product_id.filtered(
                lambda product: product.branch_id
                and product.branch_id != order.branch_id
            )
            if mismatched_products:
                raise ValidationError(
                    _(
                        "The following products belong to a different branch than the sale order branch '%(branch)s':\n%(products)s",
                        branch=order.branch_id.name,
                        products=", ".join(mismatched_products.mapped("display_name")),
                    )
                )

    def _prepare_invoice(self):
        """Include branch in the invoice preparation logic."""
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        branch_id = self.branch_id.id
        journal = self._find_journal(branch_id)

        if not journal:
            raise UserError(
                _(
                    "No journal could be found for the '%s' branch "
                    "for any of the sale types.",
                    self.branch_id.name,
                )
            )

        invoice_vals.update(
            {
                "branch_id": branch_id,
                "journal_id": journal.id,
            }
        )
        return invoice_vals

    def _find_journal(self, branch_id):
        """Helper to find the correct journal for the branch."""
        domain = [
            ("branch_id", "=", branch_id),
            ("type", "=", "sale"),
            ("code", "!=", "POSS"),
            ("company_id", "=", self.company_id.id),
        ]
        journal = self.env["account.journal"].search(domain, limit=1)

        # Fallback to default branchless journal if no branch-specific journal exists
        if not journal:
            domain[0] = ("branch_id", "=", False)
            journal = self.env["account.journal"].search(domain, limit=1)

        return journal

    @api.onchange("branch_id")
    def onchange_branch_id(self):
        """Validate branch selection and ensure it is allowed for the user."""
        if (
            self.branch_id
            and self.branch_id not in self.env.user.branch_ids
            and self.env.user.branch_ids
        ):
            raise UserError(_("Unauthorized branch selected."))

        # Reset fields dependent on the branch
        self.picking_type_id = False
        self.fiscal_position_id = False


class SaleOrderLine(models.Model):
    """Extend sale.order.line to include branch-specific logic."""

    _inherit = "sale.order.line"

    branch_id = fields.Many2one(
        related="order_id.branch_id",
        string="Branch",
        store=True,
        help="The branch associated with this sale order line.",
    )
