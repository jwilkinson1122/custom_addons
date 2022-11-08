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

    left_photo = fields.Image(related="patient_id.left_photo")
    right_photo = fields.Image(related="patient_id.right_photo")
    left_obj_model = fields.Binary(related="patient_id.left_obj_model")
    right_obj_model = fields.Binary(related="patient_id.right_obj_model")
    l_foot_only = fields.Boolean('Left Only')
    r_foot_only = fields.Boolean('Right Only')
    b_l_pair = fields.Boolean('Bilateral')
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

    image = fields.Binary("Foot Image")

    diagnosis_id = fields.Many2one(
        comodel_name='podiatry.patient.diagnosis',
        string='diagnosis')

    user_id = fields.Many2one(
        'res.users', 'User', readonly=True, default=lambda self: self.env.user)

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

        company_id = fields.Many2one(
            comodel_name="res.company",
            default=lambda self: self.env.company,
            store=True,
        )

    # patient_id = fields.Many2one(
    #     comodel_name="pod.patient",
    #     default=lambda self: self.env.company,
    #     store=True,
    # )

    customer = fields.Many2one(
        'res.partner', string='Customer / Patient', readonly=False)
    # customer_age = fields.Integer(related='customer.age')
    # patient_id = fields.Many2one('pod.patient', 'Patient ID')
    prescription_date = fields.Date(
        'Prescription Date', default=fields.Datetime.now())
    device_type = fields.Many2one('device.type')
    diagnosis_client = fields.Text()
    notes_laboratory = fields.Text()
    podiatrist_observation = fields.Text()
    state = fields.Selection(
        [('Draft', 'Draft'), ('Confirm', 'Confirm')], default='Draft')

    def confirm_request(self):
        for rec in self:
            rec.state = 'Confirm'

    def default_examination_chargeable(self):
        settings_examination_chargeable = self.env['ir.config_parameter'].sudo().get_param(
            'examination_chargeable')
        return settings_examination_chargeable

    examination_chargeable = fields.Boolean(
        default=default_examination_chargeable, readonly=1)

    # prescription_type = fields.Selection(
    #     [('Internal', 'Internal'), ('External', 'External')], default='internal')

    # left, right, bilateral options

    rx_left_only = fields.Boolean()
    rx_right_only = fields.Boolean()
    rx_bilateral_copy = fields.Boolean()
    rx_bilateral_custom = fields.Boolean()

    # RX options
    left_low_profile = fields.Boolean()
    right_low_profile = fields.Boolean()

    # OD
    od_sph_distance = fields.Char(
    )
    od_sph_near = fields.Char(
    )
    od_cyl_distance = fields.Char(
    )
    od_cyl_near = fields.Char(
    )
    od_av_near = fields.Char(
    )
    os_av_near = fields.Char(
    )
    od_ax_distance = fields.Char(
    )
    od_av_distance = fields.Char(
    )
    os_av_distance = fields.Char(
    )
    os_pupillary_distance = fields.Char()
    od_pupillary_distance = fields.Char()
    os_pupillary_near = fields.Char()
    od_pupillary_near = fields.Char()
    od_ax_near = fields.Char(
    )
    od_add_distance = fields.Char(
    )
    od_add_near = fields.Char(
    )
    od_prism_distance = fields.Char(
    )
    od_prism_near = fields.Char(
    )
    od_base_distance = fields.Char(
    )
    od_base_near = fields.Char(
    )
    os_sph_distance = fields.Char(
    )
    os_sph_near = fields.Char(
    )
    os_cyl_distance = fields.Char(
    )
    os_cyl_near = fields.Char(
    )
    os_ax_distance = fields.Char(
    )
    os_ax_near = fields.Char(
    )
    os_add_distance = fields.Char(
    )
    os_add_near = fields.Char(
    )
    os_prism_distance = fields.Char(
    )
    os_prism_near = fields.Char(
    )
    os_base_distance = fields.Char(
    )
    os_base_near = fields.Char(
    )

    # Extras
    ipd = fields.Char(string="ipd")
    cl_right = fields.Char(string="Cl Right")
    cl_left = fields.Char(string="Cl Left")
    base_curve = fields.Char(string="Base Curve")
    dim = fields.Char(string="Dim")

    # ophthalmological
    r_wc_close = fields.Char()
    r_wc_far = fields.Char()
    r_woc_close = fields.Char()
    r_woc_far = fields.Char()
    r_tonometria = fields.Char()
    l_wc_close = fields.Char()
    l_wc_far = fields.Char()
    l_woc_close = fields.Char()
    l_woc_far = fields.Char()
    l_tonometria = fields.Char()
    ad_wc_close = fields.Char()
    ad_wc_far = fields.Char()
    ad_woc_close = fields.Char()
    ad_woc_far = fields.Char()
    ad_tonometria = fields.Char()
    ph = fields.Text('P.H')
    cie_10 = fields.Selection([('cataract_eye', 'Cataract Eye'), ('pterygium', "Pterygium"), ('glaucoma', 'Glaucoma'), ('squint', 'Squint'), ('detachment', 'Detachment'), (
        'laser_myopia', 'laser_myopia'), ('ocular_prosthesis', 'Ocular Prosthesis'), ('chalazion', 'Chalazion'), ('conjunctivitis', 'Conjunctivitis')], string='CIE 10')
    main_symptoms = fields.Text('Main Symptoms')
    background = fields.Text('Background')
    opthalmological_exam = fields.Text('Opthalmological Exam')
    treatment = fields.Text('Treatment')
    other_exams = fields.Text('Other Exams')
    observations = fields.Text('Observations')
    podiatry_history = fields.Text()
    ocular_history = fields.Text()
    consultation = fields.Text()

    # pdl = fields.Selection(
    #     [
    #         ('25', '25'), ('25.5', '25.5'), ('26', '26'), ('26.5', '26.5'), ('27', '27'),
    #         ('27.5', '27.5'),
    #         ('28', '28'), ('28.5', '28.5'), ('29', '29'), ('29.5', '29.5'),
    #         ('30', '30'), ('30.5', '30.5'), ('31', '31'), ('31.5', '31.5'), ('32', '32'),
    #         ('32.5', '32.5'),
    #         ('33', '33'), ('33.5', '33.5'), ('34', '34'), ('34.5', '34.5'), ('35', '35'),
    #         ('35.5', '35.5'), ('36', '36'), ('36.5', '36.5'), ('37', '37'), ('37.5', '37.5'),
    #         ('38', '38'), ('38.5', '38.5'), ('39', '39'),
    #         ('39.5', '39.5'), ('40', '40')
    #
    #
    #      ],default='25')
    # pdr = fields.Selection(
    #     [
    #         ('25', '25'), ('25.5', '25.5'), ('26', '26'),('26.5', '26.5'), ('27', '27'),('27.5', '27.5'),
    #         ('28', '28'),('28.5', '28.5'),('29', '29'),('29.5', '29.5'),
    #         ('30', '30'),('30.5', '30.5'), ('31', '31'),('31.5', '31.5'), ('32', '32'),
    #         ('32.5', '32.5'),
    #         ('33', '33'),('33.5','33.5'), ('34', '34'),('34.5', '34.5'), ('35', '35'),('35.5', '35.5'), ('36', '36'),('36.5', '36.5'), ('37', '37'),('37.5', '37.5'),('38','38'),('38.5','38.5'), ('39','39'),
    #         ('39.5','39.5'),('40','40')
    #
    #
    #      ],default='25')
    # Not required
    # prism = fields.Boolean('Prism')
    # prisml = fields.Float('Prism')
    # dim = fields.Float('Dim')
    # diml = fields.Float('Dim')
    # height = fields.Float('Height')
    # heightl = fields.Float('Height')
    # basel = fields.Selection(
    #     [('Select', 'Select'), ('IN', 'IN'), ('OUT', 'OUT'), ('UP', 'UP'), ('DOWN', 'DOWN'),
    #      ], 'basel')
    # prism_vall = fields.Selection(
    #     [('0.25', '0.25'), ('0.5', '0.5'), ('0.75', '0.75'), ('1', '1'),
    #      ('1.25', '1.25'), ('1.5', '1.5'),
    #      ('1.75', '1.75'), ('2', '2'), ('2.25', '2.25'), ('2.5', '2.5'), ('2.75', '2.75'),
    #      ('3', '3'), ('3.25', '3.25'), ('3.5', '3.5'), ('3.75', '3.75'), ('4', '4'), ('4.25', '4.25'),
    #      ('4.5', '4.5'), ('4.75', '4.75'),
    #      ('5', '5')], 'PrismL')
    # lpd = fields.Float('lpd')
    # lpdl = fields.Float('lpd')
    # dual_pd = fields.Boolean('I have Dual PD')
    # pd_distance = fields.Selection(
    #     [('47', '47'), ('48', '48'), ('49', '49'), ('50', '50'),
    #      ('60', '60'), ('70', '70')
    #         , ('79', '79')], 'PD')
    # pd_near = fields.Selection(
    #     [('47', '47'), ('48', '48'), ('49', '49'), ('50', '50'),
    #      ('60', '60'), ('70', '70')
    #         , ('79', '79')], 'PD')

    dr_notes = fields.Text('Notes')
    name = fields.Char(required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    family_history = fields.Text()
    ocular_history = fields.Text()
    consultation = fields.Text()

    @api.onchange('os_sph_distance', 'od_sph_distance')
    def onchange_sph_distance(self):
        if self.os_sph_distance and self.os_sph_distance.isdigit():
            self.os_sph_distance = "+" + \
                "{:.2f}".format(float(self.os_sph_distance))
        elif self.os_sph_distance:
            if '-' in self.os_sph_distance:
                self.os_sph_distance = "{:.2f}".format(
                    float(self.os_sph_distance))
        if self.od_sph_distance and self.od_sph_distance.isdigit():
            self.od_sph_distance = "+" + \
                "{:.2f}".format(float(self.od_sph_distance))
        elif self.od_sph_distance:
            if '-' in self.od_sph_distance:
                self.od_sph_distance = "{:.2f}".format(
                    float(self.od_sph_distance))

    @api.onchange('os_sph_near', 'od_sph_near')
    def onchange_sph_near(self):
        if self.os_sph_near and self.os_sph_near.isdigit():
            self.os_sph_near = "+" + "{:.2f}".format(float(self.os_sph_near))
        elif self.os_sph_near:
            if '-' in self.os_sph_near:
                self.os_sph_near = "{:.2f}".format(float(self.os_sph_near))
        if self.od_sph_near and self.od_sph_near.isdigit():
            self.od_sph_near = "+" + "{:.2f}".format(float(self.od_sph_near))
        elif self.od_sph_near:
            if '-' in self.od_sph_near:
                self.od_sph_near = "{:.2f}".format(float(self.od_sph_near))

    @api.onchange('od_cyl_distance', 'os_cyl_distance')
    def onchange_cyl_distance(self):
        if self.od_cyl_distance and self.od_cyl_distance.isdigit():
            self.od_cyl_distance = "+" + \
                "{:.2f}".format(float(self.od_cyl_distance))
        elif self.od_cyl_distance:
            if '-' in self.od_cyl_distance:
                self.od_cyl_distance = "{:.2f}".format(
                    float(self.od_cyl_distance))
        if self.os_cyl_distance and self.os_cyl_distance.isdigit():
            self.os_cyl_distance = "+" + \
                "{:.2f}".format(float(self.os_cyl_distance))
        elif self.os_cyl_distance:
            if '-' in self.os_cyl_distance:
                self.os_cyl_distance = "{:.2f}".format(
                    float(self.os_cyl_distance))

    @api.onchange('od_cyl_near', 'os_cyl_near')
    def onchange_cyl_near(self):
        if self.od_cyl_near and self.od_cyl_near.isdigit():
            self.od_cyl_near = "+" + "{:.2f}".format(float(self.od_cyl_near))
        elif self.od_cyl_near:
            if '-' in self.od_cyl_near:
                self.od_cyl_near = "{:.2f}".format(float(self.od_cyl_near))
        if self.os_cyl_near and self.os_cyl_near.isdigit():
            self.os_cyl_near = "+" + "{:.2f}".format(float(self.os_cyl_near))
        elif self.os_cyl_near:
            if '-' in self.os_cyl_near:
                self.os_cyl_near = "{:.2f}".format(float(self.os_cyl_near))

    @api.onchange('od_add_distance', 'os_add_distance')
    def onchange_add_distance(self):
        if self.od_add_distance and self.od_add_distance.isdigit():
            self.od_add_distance = "+" + \
                "{:.2f}".format(float(self.od_add_distance))
            value = "{:.2f}".format(
                float(self.od_sph_distance) + float(self.od_add_distance))
            self.od_sph_near = value if '-' in value else "+" + value
            self.od_cyl_near = self.od_cyl_distance
            self.od_ax_near = self.od_ax_distance
        if self.od_add_distance:
            if '-' in self.od_add_distance:
                self.od_add_distance = "{:.2f}".format(
                    float(self.od_add_distance))
                value = "{:.2f}".format(
                    float(self.od_sph_distance) + float(self.od_add_distance))
                self.od_sph_near = value if '-' in value else "+" + value
                self.od_cyl_near = self.od_cyl_distance
                self.od_ax_near = self.od_ax_distance
        if self.os_add_distance and self.os_add_distance.isdigit():
            self.os_add_distance = "+" + \
                "{:.2f}".format(float(self.os_add_distance))
            value = "{:.2f}".format(
                float(self.os_sph_distance) + float(self.os_add_distance))
            self.os_sph_near = value if '-' in value else "+" + value
            self.os_cyl_near = self.os_cyl_distance
            self.os_ax_near = self.os_ax_distance
        if self.os_add_distance:
            if '-' in self.os_add_distance:
                self.os_add_distance = "{:.2f}".format(
                    float(self.os_add_distance))
                value = "{:.2f}".format(
                    float(self.os_sph_distance) + float(self.os_add_distance))
                self.os_sph_near = value if '-' in value else "+" + value
                self.os_cyl_near = self.os_cyl_distance
                self.os_ax_near = self.os_ax_distance

    @api.onchange('od_av_distance', 'os_av_distance')
    def onchange_av_distance(self):
        if self.od_av_distance and self.od_av_distance.isdigit():
            self.od_av_distance = "20/" + self.od_av_distance
        if self.os_av_distance and self.os_av_distance.isdigit():
            self.os_av_distance = "20/" + self.os_av_distance

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
                # 'context':{'default_dr':self.id},
                'type': 'ir.actions.act_window',
            }

        else:
            return {
                'name': _('Practitioner Prescription'),
                'view_type': 'form',
                'res_model': 'sale.order',
                'view_id': False,
                'view_mode': 'form',
                'context': {'default_prescription_id': self.id, 'default_partner_id': self.customer.id},
                'type': 'ir.actions.act_window',
            }

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

    # def print_prescription_report(self):
    #     return {
    #         'type': 'ir.actions.report',
    #         'report_name': "podiatry.practitioner_prescription_template",
    #         'report_file': "podiatry.practitioner_prescription_template",
    #         'report_type': 'qweb-pdf',
    #     }

    def print_prescription_report_ticket_size(self):
        return self.env.ref("podiatry.practitioner_prescription_ticket_size2").report_action(self)

    # def print_prescription_report(self):
    #     return {
    #         'type': 'ir.actions.report',
    #         'report_name': "podiatry.practitioner_prescription_template",
    #         'report_file': "podiatry.practitioner_prescription_template",
    #         'report_type': 'qweb-pdf',
    #     }

    # def print_prescription_report_ticket_size(self):
    #     return self.env.ref("podiatry.practitioner_prescription_ticket_size2").report_action(self)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
