import time
from datetime import timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import get_lang


class Prescription(models.Model):
    _name = 'podiatry.prescription'
    _description = 'Prescription Request'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.depends('patient_id')
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
        Stage = self.env["podiatry.prescription.stage"]
        return Stage.search([("state", "=", "new")], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    active = fields.Boolean(default=True)
    color = fields.Integer()
    date = fields.Date()
    time = fields.Datetime()

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string='Practice')

    practitioner_id = fields.Many2one(
        comodel_name='podiatry.practitioner',
        string='Practitioner')

    practitioner_phone = fields.Char(
        string='Phone', related='practitioner_id.phone')
        
    practitioner_email = fields.Char(
        string='Email', related='practitioner_id.email')

    patient_id = fields.Many2one(
        comodel_name='podiatry.patient',
        string='Patient')

#    right_photo = fields.Image("Right Photo")
#     left_photo = fields.Image("Left Photo")


    # right_photo = fields.Image("Right Photo")
    # left_photo = fields.Image("Left Photo")
    # left_obj_model = fields.Binary("Left Obj")
    # left_obj_file_name = fields.Char(string="Left Obj File Name")
    # right_obj_model = fields.Binary("Right Obj")
    # right_obj_file_name = fields.Char(string="Right Obj File Name")


    left_photo = fields.Image(related="patient_id.left_photo")
    right_photo = fields.Image(related="patient_id.right_photo")
    left_obj_model = fields.Binary(related="patient_id.left_obj_model")
    right_obj_model = fields.Binary(related="patient_id.right_obj_model")


    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], related='patient_id.gender')

    patient_phone = fields.Char(string='Phone', related='patient_id.phone')
    patient_email = fields.Char(string='Email', related='patient_id.email')
    # patient_age = fields.Integer(string='Age', related='patient_id.age')

    description = fields.Text(string='Description')

    image = fields.Binary("Foot Image")

    diagnosis_id = fields.Many2one(
        comodel_name='podiatry.patient.diagnosis',
        string='diagnosis')

    user_id = fields.Many2one(
        'res.users', 'Login User', readonly=True, default=lambda self: self.env.user)

    attachment_ids = fields.Many2many('ir.attachment', 'prescription_ir_attachments_rel',
                                      'manager_id', 'attachment_id', string="Attachments",
                                      help="Images/attachments before prescription")

    inv_state = fields.Selection(
        [('invoiced', 'To Invoiced'), ('tobe', 'To Be Invoiced')], 'Invoice Status')

    no_invoice = fields.Boolean('Invoice exempt')

    inv_id = fields.Many2one('account.invoice', 'Invoice')

    prescription = fields.Text(string="Prescription")

    prescription_ids = fields.One2many(
        'podiatry.prescription', 'patient_id', string="Prescriptions")

    prescription_line_ids = fields.One2many(
        'podiatry.prescription.line', 'prescription_id', 'Prescription Line')

     

    # state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
    #                           ('done', 'Done'), ('cancel', 'Cancelled')], default='draft',
    #                          string="Status", tracking=True)

    completed_date = fields.Datetime(string="Completed Date")

    request_date = fields.Date(
        default=lambda s: fields.Date.today(),
        compute="_compute_request_date_onchange",
        store=True,
        readonly=False,
    )

    stage_id = fields.Many2one(
        "podiatry.prescription.stage",
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

    @api.model
    def _get_bookin_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        checkin_date = fields.Datetime.context_timestamp(
            self, fields.Datetime.now())
        return fields.Datetime.to_string(checkin_date)

    @api.model
    def _get_bookout_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        checkout_date = fields.Datetime.context_timestamp(
            self, fields.Datetime.now() + timedelta(days=1)
        )
        return fields.Datetime.to_string(checkout_date)

    prescription_date = fields.Date(readonly=True)

    close_date = fields.Date(readonly=True)

    bookin_date = fields.Datetime(
        "Book In",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_get_bookin_date,
    )
    bookout_date = fields.Datetime(
        "Book Out",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_get_bookout_date,
    )

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')

    def _compute_prescription_count_DISABLED(self):
        "Naive version, not performance optimal"
        for prescription in self:
            domain = [
                ("practitioner_id", "=", prescription.practitioner_id.id),
                ("state", "not in", ["done", "cancel"]),
            ]
            prescription.prescription_count = self.search_count(domain)

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['podiatry.prescription'].search_count(
                [('practitioner_id', '=', rec.id), ("state", "not in", ["done", "cancel"]), ])
            rec.prescription_count = prescription_count

    # def _compute_prescription_count(self):
    #     "Performance optimized, to run a single database query"
    #     practitioners = self.mapped("practitioner_id")
    #     domain = [
    #         ("practitioner_id", "in", practitioners.ids),
    #         ("state", "not in", ["done", "cancel"]),
    #     ]
    #     raw = self.read_group(domain, ["id:count"], ["practitioner_id"])
    #     data = {x["practitioner_id"][0]: x["practitioner_id"] for x in raw}
    #     for prescription in self:
    #         prescription.prescription_count = data.get(
    #             prescription.practitioner_id.id, 0)

    num_prescriptions = fields.Integer(
        compute="_compute_num_prescriptions", store=True)

    @api.depends("prescription_line_ids")
    def _compute_num_prescriptions(self):
        for prescription in self:
            prescription.num_prescriptions = len(
                prescription.prescription_line_ids)

    invoice_done = fields.Boolean('Invoice Done')

    notes = fields.Text('Prescription Note')

    is_invoiced = fields.Boolean(copy=False, default=False)

    is_shipped = fields.Boolean(default=False, copy=False)

    def action_confirm(self):
        self.state = 'confirm'

    def action_done(self):
        self.state = 'done'

    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'podiatry.prescription') or _('New')
        res = super(Prescription, self).create(vals)
        if res.stage_id.state in ("open", "close"):
            raise exceptions.UserError(
                "State not allowed for new prescriptions."
            )
        return res

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

    def prescription_report(self):
        return self.env.ref('podiatry.report_print_prescription').report_action(self)

        # Replaced by _compute_request_date_onchange
    # @api.onchange('patient_id')
    # def onchange_patient_id(self):
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
        Stage = self.env["podiatry.prescription.stage"]
        done_stage = Stage.search([("state", "=", "done")], limit=1)
        for prescription in self:
            prescription.stage_id = done_stage
        return True

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            if self.patient_id.gender:
                self.gender = self.patient_id.gender
            if self.patient_id.notes:
                self.notes = self.patient_id.notes
        else:
            self.gender = ''
            self.notes = ''

    def unlink(self):
        if self.state == 'done':
            raise ValidationError(
                _("You Cannot Delete %s as it is in Done State" % self.name))
        return super(Prescription, self).unlink()

    def action_url(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://nwpodiatric.com' % self.prescription,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
