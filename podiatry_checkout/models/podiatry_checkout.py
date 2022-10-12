from odoo import api, exceptions, fields, models


class Checkout(models.Model):
    _name = "podiatry.checkout"
    _description = "Checkout Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.depends('practitioner_id')
    def _compute_request_date_onchange(self):
        today_date = fields.Date.today()
        if self.request_date != today_date:
            self.request_date = today_date
            return {
                "warning": {
                    "title": "Changed Request Date",
                    "message": "Request date changed to today!",
                }
            }

    @api.model
    def _default_stage(self):
        Stage = self.env["podiatry.checkout.stage"]
        return Stage.search([("state", "=", "new")], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    name = fields.Char(string="Title")
    practitioner_image = fields.Binary(related="practitioner_id.image_128")

    practitioner_id = fields.Many2one("podiatry.practitioner", required=True)
    user_id = fields.Many2one("res.users", "Librarian",
                              default=lambda s: s.env.user)
    line_ids = fields.One2many(
        "podiatry.checkout.line",
        "checkout_id",
        string="Borrowed Prescriptions",
    )

    request_date = fields.Date(
        default=lambda s: fields.Date.today(),
        compute="_compute_request_date_onchange",
        store=True,
        readonly=False,
    )

    stage_id = fields.Many2one(
        "podiatry.checkout.stage",
        default=_default_stage,
        copy=False,
        group_expand="_group_expand_stage_id")
    state = fields.Selection(related="stage_id.state")
    kanban_state = fields.Selection(
        [("normal", "In Progress"),
         ("blocked", "Blocked"),
         ("done", "Ready for next stage")],
        "Kanban State",
        default="normal")
    color = fields.Integer()
    priority = fields.Selection(
        [("0", "High"),
         ("1", "Very High"),
         ("2", "Critical")],
        default="0")

    checkout_date = fields.Date(readonly=True)
    close_date = fields.Date(readonly=True)

    count_checkouts = fields.Integer(
        compute="_compute_count_checkouts")

    def _compute_count_checkouts_DISABLED(self):
        "Naive version, not performance optimal"
        for checkout in self:
            domain = [
                ("practitioner_id", "=", checkout.practitioner_id.id),
                ("state", "not in", ["done", "cancel"]),
            ]
            checkout.count_checkouts = self.search_count(domain)

    def _compute_count_checkouts(self):
        "Performance optimized, to run a single database query"
        practitioners = self.mapped("practitioner_id")
        domain = [
            ("practitioner_id", "in", practitioners.ids),
            ("state", "not in", ["done", "cancel"]),
        ]
        raw = self.read_group(domain, ["id:count"], ["practitioner_id"])
        data = {x["practitioner_id"][0]: x["practitioner_id_count"]
                for x in raw}
        for checkout in self:
            checkout.count_checkouts = data.get(checkout.practitioner_id.id, 0)

    num_prescriptions = fields.Integer(
        compute="_compute_num_prescriptions", store=True)

    @api.depends("line_ids")
    def _compute_num_prescriptions(self):
        for prescription in self:
            prescription.num_prescriptions = len(prescription.line_ids)

    @api.model
    def create(self, vals):
        # Code before create: should use the `vals` dict
        new_record = super().create(vals)
        # Code after create: can use the `new_record` created
        if new_record.stage_id.state in ("open", "close"):
            raise exceptions.UserError(
                "State not allowed for new checkouts."
            )
        return new_record

    def write(self, vals):
        # reset kanban state when changing stage
        if "stage_id" in vals and "kanban_state" not in vals:
            vals["kanban_state"] = "normal"
        # Code before write: `self` has the old values
        old_state = self.stage_id.state
        super().write(vals)
        # Code after write: can use `self` with the updated values
        new_state = self.stage_id.state
        if not self.env.context.get("_checkout_write"):
            if new_state != old_state and new_state == "open":
                self.with_context(_checkout_write=True).write(
                    {"checkout_date": fields.Date.today()})
            if new_state != old_state and new_state == "done":
                self.with_context(_checkout_write=True).write(
                    {"close_date": fields.Date.today()})
        return True

    # Replaced by _compute_request_date_onchange
    # @api.onchange('practitioner_id')
    # def onchange_practitioner_id(self):
    #    today_date = fields.Date.today()
    #    if self.request_date != today_date:
    #        self.request_date = today_date
    #        return {
    #            'warning': {
    #                'title': 'Changed Request Date',
    #                'message': 'Request date changed to today!',
    #            }
    #        }

    def button_done(self):
        Stage = self.env["podiatry.checkout.stage"]
        done_stage = Stage.search([("state", "=", "done")], limit=1)
        for checkout in self:
            checkout.stage_id = done_stage
        return True
