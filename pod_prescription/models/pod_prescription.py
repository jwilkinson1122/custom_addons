from odoo import api, exceptions, fields, models


class Prescription(models.Model):
    _name = "pod.prescription"
    _description = "Prescription Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.depends('member_id')
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
        Stage = self.env["pod.prescription.stage"]
        return Stage.search([("state", "=", "new")], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    name = fields.Char(string="Title")
    member_image = fields.Binary(related="member_id.image_128")

    member_id = fields.Many2one("pod.member", required=True)
    user_id = fields.Many2one("res.users", "User",
                              default=lambda s: s.env.user)
    line_ids = fields.One2many(
        "pod.prescription.line",
        "prescription_id",
        string="Patient Prescriptions",
    )

    request_date = fields.Date(
        default=lambda s: fields.Date.today(),
        compute="_compute_request_date_onchange",
        store=True,
        readonly=False,
    )

    stage_id = fields.Many2one(
        "pod.prescription.stage",
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

    prescription_date = fields.Date(readonly=True)
    close_date = fields.Date(readonly=True)

    count_prescriptions = fields.Integer(
        compute="_compute_count_prescriptions")

    def _compute_count_prescriptions_DISABLED(self):
        "Naive version, not performance optimal"
        for prescription in self:
            domain = [
                ("member_id", "=", prescription.member_id.id),
                ("state", "not in", ["done", "cancel"]),
            ]
            prescription.count_prescriptions = self.search_count(domain)

    def _compute_count_prescriptions(self):
        "Performance optimized, to run a single database query"
        members = self.mapped("member_id")
        domain = [
            ("member_id", "in", members.ids),
            ("state", "not in", ["done", "cancel"]),
        ]
        raw = self.read_group(domain, ["id:count"], ["member_id"])
        data = {x["member_id"][0]: x["member_id_count"] for x in raw}
        for prescription in self:
            prescription.count_prescriptions = data.get(
                prescription.member_id.id, 0)

    num_patients = fields.Integer(compute="_compute_num_patients", store=True)

    @api.depends("line_ids")
    def _compute_num_patients(self):
        for patient in self:
            patient.num_patients = len(patient.line_ids)

    @api.model
    def create(self, vals):
        # Code before create: should use the `vals` dict
        new_record = super().create(vals)
        # Code after create: can use the `new_record` created
        if new_record.stage_id.state in ("open", "close"):
            raise exceptions.UserError(
                "State not allowed for new prescriptions."
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
        if not self.env.context.get("_prescription_write"):
            if new_state != old_state and new_state == "open":
                self.with_context(_prescription_write=True).write(
                    {"prescription_date": fields.Date.today()})
            if new_state != old_state and new_state == "done":
                self.with_context(_prescription_write=True).write(
                    {"close_date": fields.Date.today()})
        return True

    # Replaced by _compute_request_date_onchange
    # @api.onchange('member_id')
    # def onchange_member_id(self):
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
        Stage = self.env["pod.prescription.stage"]
        done_stage = Stage.search([("state", "=", "done")], limit=1)
        for prescription in self:
            prescription.stage_id = done_stage
        return True
