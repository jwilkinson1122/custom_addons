import time
import json
from datetime import timedelta
from odoo import _, api, fields, models, exceptions
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import get_lang


class Prescription(models.Model):
    _name = 'podiatry.prescription'
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
        Stage = self.env["podiatry.prescription.stage"]
        return Stage.search([("state", "=", "draft")], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    name = fields.Char(string='Order Reference', required=True,
                       copy=False, index=True, readonly=True, default=lambda self: _('New'))

    active = fields.Boolean(default=True)
    color = fields.Integer()
    date = fields.Date()
    time = fields.Datetime()
    invoice_done = fields.Boolean('Invoice Done')
    notes = fields.Text('Prescription Note')
    is_invoiced = fields.Boolean(copy=False, default=False)
    is_shipped = fields.Boolean(default=False, copy=False)
    diagnosis_client = fields.Text()
    notes_laboratory = fields.Text()
    podiatrist_observation = fields.Text()
    dr_notes = fields.Text('Notes')
    measure_notes = fields.Text('Internal Notes')
    podiatric_history = fields.Text()

    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company, store=True)

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice', string='Practice', states={"draft": [("readonly", False)], "done": [("readonly", True)]})

    practice_name = fields.Char(
        string='Practitioner', related='practice_id.name')

    practitioner_id = fields.Many2one(
        comodel_name='podiatry.practitioner', string='Practitioner', states={"draft": [("readonly", False)], "done": [("readonly", True)]})

    practitioner_name = fields.Char(
        string='Practitioner', related='practitioner_id.name')

    practitioner_phone = fields.Char(
        string='Phone', related='practitioner_id.phone')

    practitioner_email = fields.Char(
        string='Email', related='practitioner_id.email')

    patient_id = fields.Many2one(
        comodel_name='podiatry.patient', string='Patient', states={"draft": [("readonly", False)], "done": [("readonly", True)]})

    patient_name = fields.Char(
        string='Practitioner', related='patient_id.name')

    # patient_prescription_id = fields.One2many(
    #     comodel_name='podiatry.prescription',
    #     inverse_name='patient_id',

    # )

    test_file = fields.Binary(string='Test')

    foot_image1 = fields.Binary(related="patient_id.image1")
    foot_image2 = fields.Binary(related="patient_id.image2")

    left_obj_model = fields.Binary(related="patient_id.left_obj_model")
    right_obj_model = fields.Binary(related="patient_id.right_obj_model")

    foot_selection = fields.Selection([('left_only', 'Left Only'), (
        'right_only', 'Right Only'), ('bilateral', 'Bilateral')], default='bilateral')

    left_only = fields.Boolean('Left Only')
    right_only = fields.Boolean('Right Only')

    left_low_profile = fields.Boolean()
    right_low_profile = fields.Boolean()

    shell_foundation = fields.Selection([('cataract_eye', 'Cataract Eye'), ('pterygium', "Pterygium"), ('glaucoma', 'Glaucoma'), ('squint', 'Squint'), ('detachment', 'Detachment'), (
        'laser_myopia', 'laser_myopia'), ('ocular_prosthesis', 'Ocular Prosthesis'), ('chalazion', 'Chalazion'), ('conjunctivitis', 'Conjunctivitis')], string='CIE 10')

    rush_order = fields.Boolean('3-day rush')
    make_from_prior_rx = fields.Boolean('Make From Prior Rx#:')
    qty = fields.Integer('pairs to make')
    ship_to_patient = fields.Boolean('Ship to patient')

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], related='patient_id.gender')

    patient_phone = fields.Char(string='Phone', related='patient_id.phone')
    patient_email = fields.Char(string='Email', related='patient_id.email')
    # patient_age = fields.Integer(string='Age', related='patient_id.age')

    description = fields.Text(string='Description')

    diagnosis_id = fields.Many2one(
        comodel_name='podiatry.patient.diagnosis', string='diagnosis')

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
        'podiatry.prescription', 'practitioner_id', string="Prescriptions")

    prescription_line = fields.One2many(
        'podiatry.prescription.line', 'prescription_id', 'Prescription Lines')

    prior_rx = fields.Boolean('Use Prior Rx#')

    product_id = fields.Many2one('product.product', 'Name')

    completed_date = fields.Datetime(string="Completed Date")

    request_date = fields.Date(default=lambda s: fields.Date.today(
    ), compute="_compute_request_date_onchange", store=True, readonly=False)

    stage_id = fields.Many2one("podiatry.prescription.stage", default=_default_stage,
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

    @api.depends("prescription_line")
    def _compute_num_prescription_items(self):
        for prescription in self:
            prescription.num_prescription_items = len(
                prescription.prescription_line)

    def action_draft(self):
        self.state = 'draft'

    # def action_check(self):
    #     self.state = 'in_process'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def action_hold(self):
        self.state = 'hold'

    def confirm_draft(self):
        for rec in self:
            rec.state = 'draft'

    def default_examination_chargeable(self):
        settings_examination_chargeable = self.env['ir.config_parameter'].sudo().get_param(
            'examination_chargeable')
        return settings_examination_chargeable

    examination_chargeable = fields.Boolean(
        default=default_examination_chargeable, readonly=1)

    @api.onchange('practice_id')
    def onchange_practice_id(self):
        for rec in self:
            return {'domain': {'practitioner_id': [('practice_id', '=', rec.practice_id.id)]}}

    @api.onchange('practitioner_id')
    def onchange_practitioner_id(self):
        for rec in self:
            return {'domain': {'patient_id': [('practitioner_id', '=', rec.practitioner_id.id)]}}

    # Forefoot Values
    ff_varus_lt = fields.Many2one(
        'podiatry.forefoot.value', rel='rx_ff_varus_lt', ondelete='restrict', copy=True)
    ff_varus_rt = fields.Many2one(
        'podiatry.forefoot.value', rel='rx_ff_varus_rt', ondelete='restrict', copy=True)
    ff_valgus_lt = fields.Many2one(
        'podiatry.forefoot.value', rel='rx_ff_valgus_lt', ondelete='restrict', copy=True)
    ff_valgus_rt = fields.Many2one(
        'podiatry.forefoot.value', rel='rx_ff_valgus_rt', ondelete='restrict', copy=True)

    # Forefoot Corrections
    ff_varus_intrinsic_lt = fields.Many2one(
        'podiatry.forefoot.correction', rel='rx_ff_varus_intrinsic_lt', ondelete='restrict', copy=True)
    ff_varus_intrinsic_rt = fields.Many2one(
        'podiatry.forefoot.correction', rel='rx_ff_varus_intrinsic_rt', ondelete='restrict', copy=True)
    ff_varus_extrinsic_lt = fields.Many2one(
        'podiatry.forefoot.correction', rel='rx_ff_varus_extrinsic_lt', ondelete='restrict', copy=True)
    ff_varus_extrinsic_rt = fields.Many2one(
        'podiatry.forefoot.correction', rel='rx_ff_varus_extrinsic_rt', ondelete='restrict', copy=True)
    ff_valgus_intrinsic_lt = fields.Many2one(
        'podiatry.forefoot.correction', rel='rx_ff_valgus_intrinsic_lt', ondelete='restrict', copy=True)
    ff_valgus_intrinsic_rt = fields.Many2one(
        'podiatry.forefoot.correction', rel='rx_ff_valgus_intrinsic_rt', ondelete='restrict', copy=True)
    ff_valgus_extrinsic_lt = fields.Many2one(
        'podiatry.forefoot.correction', rel='rx_ff_valgus_extrinsic_lt', ondelete='restrict', copy=True)
    ff_valgus_extrinsic_rt = fields.Many2one(
        'podiatry.forefoot.correction', rel='rx_ff_valgus_extrinsic_rt', ondelete='restrict', copy=True)

    # Rearfoot Corrections
    rf_varus_lt = fields.Many2one(
        'podiatry.rearfoot.correction', rel='rx_rf_varus_lt', ondelete='restrict', copy=True)
    rf_varus_rt = fields.Many2one(
        'podiatry.rearfoot.correction', rel='rx_rf_varus_rt', ondelete='restrict', copy=True)
    rf_valgus_lt = fields.Many2one(
        'podiatry.rearfoot.correction', rel='rx_rf_valgus_lt', ondelete='restrict', copy=True)
    rf_valgus_rt = fields.Many2one(
        'podiatry.rearfoot.correction', rel='rx_rf_valgus_rt', ondelete='restrict', copy=True)
    rf_neutral_lt = fields.Many2one(
        'podiatry.rearfoot.correction', rel='rx_rf_neutral_lt', ondelete='restrict', copy=True)
    rf_neutral_rt = fields.Many2one(
        'podiatry.rearfoot.correction', rel='rx_rf_neutral_rt', ondelete='restrict', copy=True)

    # Orthotic Measures
    ff_length_lt = fields.Many2one(
        'podiatry.orthotic.measure', rel='rx_ff_length_lt', ondelete='restrict', copy=True)
    ff_length_rt = fields.Many2one(
        'podiatry.orthotic.measure', rel='rx_ff_length_rt', ondelete='restrict', copy=True)
    heel_depth_lt = fields.Many2one(
        'podiatry.orthotic.measure', rel='rx_heel_depth_lt', ondelete='restrict', copy=True)
    heel_depth_rt = fields.Many2one(
        'podiatry.orthotic.measure', rel='rx_heel_depth_rt', ondelete='restrict', copy=True)
    orthotic_length_lt = fields.Many2one(
        'podiatry.orthotic.measure', rel='rx_orthotic_length_lt', ondelete='restrict', copy=True)
    orthotic_length_rt = fields.Many2one(
        'podiatry.orthotic.measure', rel='rx_orthotic_length_rt', ondelete='restrict', copy=True)
    cap_size_lt = fields.Many2one(
        'podiatry.orthotic.measure', rel='rx_cap_size_lt', ondelete='restrict', copy=True)
    cap_size_rt = fields.Many2one(
        'podiatry.orthotic.measure', rel='rx_cap_size_rt', ondelete='restrict', copy=True)

    def open_customer(self):
        sale_order = self.env['sale.order'].search(
            [('prescription_id', '=', self.id)], limit=1)
        print('fire', sale_order)
        if sale_order:
            return {
                'name': _('Practitioner Prescription'),
                'view_type': 'form',
                'res_id': sale_order.id,
                'res_model': 'sale.order',
                'view_id': False,
                'view_mode': 'form',
                'type': 'ir.actions.act_window',
            }

        else:
            return {
                'name': _('Practitioner Prescription'),
                'view_type': 'form',
                'res_model': 'sale.order',
                'view_id': False,
                'view_mode': 'form',
                'context': {'default_prescription_id': self.id, 'default_partner_id': self.practitioner_id.id},
                'type': 'ir.actions.act_window',
            }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'podiatry.prescription') or _('New')
        res = super(Prescription, self).create(vals)
        if res.stage_id.state in ("done", "cancel"):
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
        return self.env.ref('podiatry.report_print_prescription').report_action(self)

    def button_done(self):
        Stage = self.env["podiatry.prescription.stage"]
        done_stage = Stage.search([("state", "=", "done")], limit=1)
        for prescription in self:
            prescription.stage_id = done_stage
        return True

    def button_hold(self):
        Stage = self.env["podiatry.prescription.stage"]
        hold_stage = Stage.search([("state", "=", "hold")], limit=1)
        for prescription in self:
            prescription.stage_id = hold_stage
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

    def print_prescription_report_ticket_size(self):
        return self.env.ref("podiatry.practitioner_prescription_ticket_size2").report_action(self)

    # def print_prescription_report(self):
    #     return {
    #         'type': 'ir.actions.report',
    #         'report_name': "podiatry.practitioner_prescription_template",
    #         'report_file': "podiatry.practitioner_prescription_template",
    #         'report_type': 'qweb-pdf',
    #     }

    def print_podiatry_prescription_report_ticket_size(self):
        return self.env.ref("podiatry.practitioner_prescription_podiatry_ticket_size2").report_action(self)

    # def print_prescription_report(self):
    #     return {
    #         'type': 'ir.actions.report',
    #         'report_name': "podiatry.practitioner_prescription_template",
    #         'report_file': "podiatry.practitioner_prescription_template",
    #         'report_type': 'qweb-pdf',
    #     }

    # def print_prescription_report_ticket_size(self):
    #     return self.env.ref("podiatry.practitioner_prescription_ticket_size2").report_action(self)

class PrescriptionLine(models.Model):
    _name = "podiatry.prescription.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'podiatry prescription line'
    _rec_name = 'prescription_id'

    @api.depends('product_id')
    def onchange_product(self):
        for each in self:
            if each:
                self.qty_available = self.product_id.qty_available
                self.price = self.product_id.lst_price
            else:
                self.qty_available = 0
                self.price = 0.0

    prescription_id = fields.Many2one('podiatry.prescription', string='Prescription')
    product_id = fields.Many2one('product.product', string='Device')
    uom_id = fields.Many2one('uom.uom', string='Unit')
    quantity = fields.Float(string="Quantity")
    
    left_only = fields.Boolean(string='Left Only', related='prescription_id.left_only')
    right_only = fields.Boolean(string='Right Only', related='prescription_id.right_only')
    left_foot = fields.Boolean(string="LT")
    right_foot = fields.Boolean(string="RT")
    # bilateral = fields.Boolean(string="Bilateral")
    # when_take = fields.Selection([('after', 'After Eat'), ('before', 'Before Eat')])
    remark = fields.Text(string='Remark')
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

 