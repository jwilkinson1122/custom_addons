from odoo import api, fields, models


class PodiatryCoverageTemplate(models.Model):
    _name = "pod.coverage.template"
    _description = "Podiatry Coverage Template"
    _order = "payor_id,name"
    _inherit = ["pod.abstract", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Name",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    payor_id = fields.Many2one(
        string="Payor",
        comodel_name="res.partner",
        domain=[("is_payor", "=", True)],
        required=True,
        ondelete="restrict",
        index=True,
        tracking=True,
        help="Payer name",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    coverage_ids = fields.One2many(
        string="Coverage",
        comodel_name="pod.coverage",
        inverse_name="coverage_template_id",
    )
    state = fields.Selection(
        string="Coverage Status",
        required="True",
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("cancelled", "Cancelled"),
            ("entered-in-error", "Entered In Error"),
        ],
        default="draft",
        tracking=True,
        readonly=True,
        help="Current state of the coverage.",
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"]
            .sudo()
            .next_by_code("pod.coverage.template")
            or "/"
        )

    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.internal_identifier
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result

    def draft2active(self):
        self.write({"state": "active"})

    def draft2cancelled(self):
        self.write({"state": "cancelled"})

    def draft2enteredinerror(self):
        self.write({"state": "entered-in-error"})

    def active2cancelled(self):
        self.write({"state": "cancelled"})

    def active2enteredinerror(self):
        self.write({"state": "entered-in-error"})

    def cancelled2enteredinerror(self):
        self.write({"state": "entered-in-error"})

    def active2draft(self):
        self.write({"state": "draft"})

    def cancelled2draft(self):
        self.write({"state": "draft"})

    def cancelled2active(self):
        self.write({"state": "active"})
