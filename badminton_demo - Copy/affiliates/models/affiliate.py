# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessError

CONTACT_DOMAIN = lambda self: [
    ("is_company", "=", False),
    ("practice_id", "=", self.env.user.company_id.partner_id.id),
    ("type", "=", "contact"),
]


@api.model
def _lang_get(self):
    return self.env["res.lang"].get_installed()


class Affiliate(models.Model):
    _name = "affiliate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Affiliate"
    _order = "season_id asc, kind asc"

    def _compute_events_count(self):
        for affiliate in self:
            affiliate.events_count = len(affiliate.event_ids)

    def _compute_is_favorite(self):
        for affiliate in self:
            affiliate.is_favorite = self.env.user in affiliate.favorite_user_ids

    def _inverse_is_favorite(self):
        favorite_affiliates = not_fav_affiliates = self.env["affiliate"].sudo()
        for affiliate in self:
            if self.env.user in affiliate.favorite_user_ids:
                favorite_affiliates |= affiliate
            else:
                not_fav_affiliates |= affiliate

        # Affiliate User has no write access for affiliate
        not_fav_affiliates.write({"favorite_user_ids": [(4, self.env.uid)]})
        favorite_affiliates.write({"favorite_user_ids": [(3, self.env.uid)]})

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    name = fields.Char(string="Name", required=True)
    event_ids = fields.One2many(
        "affiliate.event", "affiliate_id", string="Affiliate Events"
    )
    kind = fields.Selection(
        [("men", "Men"), ("women", "Women"), ("mixed", "Mixed")],
        string="Kind",
        required=True,
        default="men",
    )
    season_id = fields.Many2one(
        "period",
        string="Season",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env["period"].search(
            [("current", "=", True)], limit=1
        ),
    )
    player_ids = fields.Many2many(
        "res.partner",
        "affiliate_player_rel",
        column1="affiliate_id",
        column2="player_id",
        string="Players",
        domain=CONTACT_DOMAIN,
    )
    responsible_id = fields.Many2one(
        "res.partner", string="Responsible", domain=CONTACT_DOMAIN
    )
    location_id = fields.Many2one(
        "res.partner",
        string="Location",
        domain=lambda self: [
            ("parent_id", "=", self.env.user.company_id.partner_id.id),
            ("type", "!=", "contact"),
        ],
    )
    referee_ids = fields.Many2many(
        "res.partner",
        "affiliate_referee_rel",
        column1="affiliate_id",
        column2="referee_id",
        string="Referees",
        domain=CONTACT_DOMAIN,
    )
    event_items_color = fields.Char(
        "Event Items Color",
        help="Color of the affiliate event items in the calendar view",
    )

    events_count = fields.Integer(
        compute="_compute_events_count", string="Events Count"
    )
    lang = fields.Selection(
        _lang_get,
        string="Language",
        default=lambda self: self.env.company.partner_id.lang,
        help="All the emails sent for this record will be translated in this language.",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    favorite_user_ids = fields.Many2many(
        "res.users",
        "affiliate_favorite_user_rel",
        "affiliate_id",
        "user_id",
        default=_get_default_favorite_user_ids,
        string="Favorite Users",
    )
    is_favorite = fields.Boolean(
        compute="_compute_is_favorite",
        inverse="_inverse_is_favorite",
        string="Show Affiliate on dashboard",
        help="Whether this Affiliate should be displayed on your dashboard.",
    )

    def write(self, vals):
        if not self.env.user.has_group("affiliates.group_affiliates_affiliate_user"):
            raise AccessError(
                _("You don't have the access rights to modify an affiliate team.")
            )
        if "event_items_color" in vals:
            self.event_ids.mapped("event_id").write(
                {"item_color": vals["event_items_color"]}
            )
        return super(Affiliate, self).write(vals)

    def unlink(self):
        self.event_ids.unlink()
        return super(Affiliate, self).unlink()

    @api.onchange("kind", "season_id")
    def _onchange_kind_season(self):
        vals = []
        if self.kind:
            vals.append(
                dict(
                    self.env["affiliate"]
                    ._fields["kind"]
                    ._description_selection(self.env)
                )[self.kind]
            )
        if self.season_id:
            vals.append(self.season_id.name)
        if vals:
            self.name = " - ".join(vals)

    def action_view_events(self):
        sudo_self = self.with_context(active_id=self.id, active_ids=self.ids).sudo()
        action = sudo_self.env.ref(
            "affiliates.action_affiliate_event_active_affiliate"
        ).read()[0]
        action["display_name"] = self.name
        return action
