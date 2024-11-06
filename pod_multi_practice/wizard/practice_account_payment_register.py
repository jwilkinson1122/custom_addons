# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    """inherited account payment register wizard models"""

    _inherit = "account.payment.register"

    practice_id = fields.Many2one("res.practice", store=True, readonly=False)
    journal_id = fields.Many2one(
        "account.journal",
        store=True,
        readonly=False,
        compute="_compute_journal_id",
        domain="[('company_id', '=', company_id), " "('type', 'in', ('bank', 'cash'))]",
    )

    @api.depends("company_id", "source_currency_id")
    def _compute_journal_id(self):
        """method to compute journal id based on current practice"""
        self.ensure_one()
        lines = self.line_ids._origin
        practice = lines.practice_id
        if practice:
            for wizard in self:
                domain = [
                    ("type", "in", ("bank", "cash")),
                    ("practice_id", "=", practice.id),
                ]

                journal = self.env["account.journal"].search(domain, limit=1)
                if not journal:
                    domain = [
                        ("type", "in", ("bank", "cash")),
                        ("practice_id", "=", False),
                    ]
                    journal = self.env["account.journal"].search(domain, limit=1)
                wizard.journal_id = journal
        else:
            res = super(AccountPaymentRegister, self)._compute_journal_id()
            return res

    def _create_payment_vals_from_wizard(self, batch_result):
        vals = super()._create_payment_vals_from_wizard(batch_result)
        vals.update({"practice_id": self.line_ids.move_id[0].practice_id.id})
        return vals
