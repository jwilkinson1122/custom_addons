from odoo import api, fields, models


class ResPartnerFlag(models.Model):
    _name = "res.partner.flag"
    _description = "Partner Flag"
    _inherit = "res.partner.abstract"

    patient_id = fields.Many2one(
        string="Patient",
        comodel_name="res.partner",
        domain=[("is_patient", "=", True)],
        required=True,
        readonly=True,
        ondelete="restrict",
        index=True,
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        index=True,
        auto_join=True,
        delegate=True,
        ondelete="restrict",
    )

    active = fields.Boolean(store=True, compute="_compute_active")
    category_id = fields.Many2one("res.partner.flag.category", required=True)
    name = fields.Char(related="category_id.name", readonly=True, store=True)
    description = fields.Text(required=True)
    closure_date = fields.Datetime(readonly=True)
    closure_uid = fields.Many2one("res.users", readonly=True, string="Closure user")

    @api.model
    def _get_partner_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("res.partner.flag") or "/"

    @api.depends("name", "partner_identifier")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.partner_identifier
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result

    @api.depends("closure_date")
    def _compute_active(self):
        for rec in self:
            rec.active = not bool(rec.closure_date)

    def close(self):
        return self.write(
            {
                "closure_date": fields.Datetime.now(),
                "closure_uid": self.env.user.id,
            }
        )
