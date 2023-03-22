import time
import json
from datetime import timedelta
from odoo import _, api, fields, models, exceptions
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import get_lang


class medical_prescription_order(models.Model):
    _name = 'medical.prescription.order'
    _description = 'Prescription Request'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

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
        Stage = self.env["medical.prescription.order.stage"]
        return Stage.search([("state", "=", "draft")], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    name = fields.Char(string='Order Reference', required=True,
                       copy=False, index=True, readonly=True, default=lambda self: _('New'))

    active = fields.Boolean(default=True)
    invoice_done = fields.Boolean('Invoice Done')
    notes = fields.Text('Prescription Note')
    is_invoiced = fields.Boolean(copy=False, default=False)
    is_shipped = fields.Boolean(default=False, copy=False)
  
    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='cascade',
                                 help='Partner-related data of the Practice')

    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company, store=True)

    practice_id = fields.Many2one(
        comodel_name='medical.practice', string='Practice', states={"draft": [("readonly", False)], "done": [("readonly", True)]})

    practitioner_id = fields.Many2one(
        comodel_name='medical.practitioner', string='Practitioner', states={"draft": [("readonly", False)], "done": [("readonly", True)]})

    patient_id = fields.Many2one(
        comodel_name='medical.patient', string='Patient', states={"draft": [("readonly", False)], "done": [("readonly", True)]})
 
     
    qty = fields.Integer('pairs to make')
    

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], related='patient_id.gender')

    condition_id = fields.Many2one(
        comodel_name='medical.patient.condition', string='Medical Condition')

    user_id = fields.Many2one(
        'res.users', 'User', readonly=True, default=lambda self: self.env.user)

    attachment_ids = fields.Many2many('ir.attachment', 'prescription_ir_attachments_rel',
                                      'manager_id', 'attachment_id', string="Attachments", help="Images/attachments before prescription")

    inv_state = fields.Selection(
        [('invoiced', 'To Invoiced'), ('tobe', 'To Be Invoiced')], 'Invoice Status')

    no_invoice = fields.Boolean('Invoice exempt')

    inv_id = fields.Many2one('account.invoice', 'Invoice')

    prescription = fields.Text(string="Prescription")

    prescription_ids = fields.One2many(
        'medical.prescription.order', 'practitioner_id', string="Prescriptions")

    prescription_line_ids = fields.One2many(
        'medical.prescription.line', 'prescription_id', 'Prescription Line')

    product_id = fields.Many2one('product.product', 'Name')

    completed_date = fields.Datetime(string="Completed Date")

    request_date = fields.Date(default=lambda s: fields.Date.today(
    ), compute="_compute_request_date_onchange", store=True, readonly=False)

    stage_id = fields.Many2one("medical.prescription.order.stage", default=_default_stage,
                               copy=False, group_expand="_group_expand_stage_id")

    state = fields.Selection(related="stage_id.state")

    kanban_state = fields.Selection(
        [("normal", "In Progress"),
         ("blocked", "Blocked"),
         ("done", "Ready for next stage")],
        "Kanban State", default="normal")

    color = fields.Integer()

    priority = fields.Selection(
        [("0", "High"),
         ("1", "Very High"),
         ("2", "Critical")], default="0")

    @api.model
    def _get_bookin_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        checkin_date = fields.Datetime.context_timestamp(
            self, fields.Datetime.now())
        return fields.Datetime.to_string(checkin_date)

    @api.model
    def _get_hold_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        hold_date = fields.Datetime.context_timestamp(
            self, fields.Datetime.now() + timedelta(days=1)
        )
        return fields.Datetime.to_string(hold_date)

    @api.model
    def _get_bookout_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        checkout_date = fields.Datetime.context_timestamp(
            self, fields.Datetime.now() + timedelta(days=1)
        )
        return fields.Datetime.to_string(checkout_date)

    prescription_date = fields.Date(
        'Prescription Date', default=fields.Datetime.now())
    
    close_date = fields.Date(readonly=True)

    bookin_date = fields.Datetime(
        "Book In", required=True, readonly=True, states={"draft": [("readonly", False)], "done": [("readonly", True)]}, default=_get_bookin_date,
    )

    hold_date = fields.Datetime(
        "Hold", readonly=True, default=_get_hold_date,
    )

    bookout_date = fields.Datetime(
        "Book Out", required=True, readonly=True, states={"draft": [("readonly", False)], "done": [("readonly", True)]}, default=_get_bookout_date,
    )

    prescription_type = fields.Selection([
        ('Custom', 'Custom'),
        ('OTC', 'OTC'),
        ('Brace', 'Brace'),
    ], default='Custom', Required=True)

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
        "Performance optimized, to run a single database query"
        practitioners = self.mapped("practitioner_id")
        domain = [
            ("practitioner_id", "in", practitioners.ids),
            ("state", "not in", ["done", "cancel"]),
        ]
        raw = self.read_group(domain, ["id:count"], ["practitioner_id"])
        data = {x["practitioner_id"][0]: x["practitioner_id_count"]
                for x in raw}
        for prescription in self:
            prescription.prescription_count = data.get(
                prescription.practitioner_id.id, 0)

    num_prescription_items = fields.Integer(
        compute="_compute_num_prescription_items", store=True)

    @api.depends("prescription_line_ids")
    def _compute_num_prescription_items(self):
        for prescription in self:
            prescription.num_prescription_items = len(
                prescription.prescription_line_ids)

    def action_draft(self):
        self.state = 'draft'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def action_hold(self):
        self.state = 'hold'


    @api.onchange('practice_id')
    def onchange_practice_id(self):
        for rec in self:
            return {'domain': {'practitioner_id': [('practice_id', '=', rec.practice_id.id)]}}

    @api.onchange('practitioner_id')
    def onchange_practitioner_id(self):
        for rec in self:
            return {'domain': {'patient_id': [('practitioner_id', '=', rec.practitioner_id.id)]}}
        
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

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'medical.prescription.order') or _('New')
        res = super(medical_prescription_order, self).create(vals)
        if res.stage_id.state in ("done", "hold", "cancel"):
            raise exceptions.UserError(
                "State not allowed for new prescriptions."
            )
        return res
    

    def write(self, vals):
        if "stage_id" in vals and "kanban_state" not in vals:
            vals["kanban_state"] = "normal"
        old_state = self.stage_id.state
        super().write(vals)
        new_state = self.stage_id.state
        if not self.env.context.get("_prescription_write"):
            if new_state != old_state and new_state == "draft":
                self.with_context(_prescription_write=True).write(
                    {"prescription_date": fields.Date.today()})
            if new_state != old_state and new_state == "done":
                self.with_context(_prescription_write=True).write(
                    {"close_date": fields.Date.today()})
            if new_state != old_state and new_state == "hold":
                self.with_context(_prescription_write=True).write(
                    {"hold_date": fields.Date.today()})
        return True

    def prescription_report(self):
        return self.env.ref('pod_hms.report_print_prescription').report_action(self)

    def button_done(self):
        Stage = self.env["medical.prescription.order.stage"]
        done_stage = Stage.search([("state", "=", "done")], limit=1)
        for prescription in self:
            prescription.stage_id = done_stage
        return True

    def button_hold(self):
        Stage = self.env["medical.prescription.order.stage"]
        hold_stage = Stage.search([("state", "=", "hold")], limit=1)
        for prescription in self:
            prescription.stage_id = hold_stage
        return True

 

    def unlink(self):
        if self.state == 'done':
            raise ValidationError(
                _("You Cannot Delete %s as it is in Done State" % self.name))
        return super(medical_prescription_order, self).unlink()

    def action_url(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://nwpodiatric.com' % self.prescription,
        }


    def prescription_report(self):
        return self.env.ref('pod_hms.report_print_prescription').report_action(self)
    

     

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

