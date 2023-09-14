

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    safe_box_move_id = fields.Many2one(
        comodel_name="safe.box.move",
        readonly=True,
        string="Move",
        copy=False,
        ondelete="restrict",
        help="Relation to the safe box move. It must be defined if an account is "
        "related to a safe box group",
    )
    safe_box_group_id = fields.Many2one(
        comodel_name="safe.box.group",
        related="safe_box_move_id.safe_box_group_id",
        store=True,
        readonly=True,
    )

    def _post_validate(self):
        """
        We check that the safe box move is defined if an account is related to a
        safe box group
        """
        for move in self:
            safe_box_group = move.safe_box_move_id.safe_box_group_id
            if move.line_ids.filtered(
                lambda r: r.account_id.safe_box_group_id
                and r.account_id.safe_box_group_id != safe_box_group
            ):
                raise ValidationError(
                    _(
                        "Accounts with a related safe box must be under safe box "
                        "moves"
                    )
                )
        super(AccountMove, self)._post_validate()
