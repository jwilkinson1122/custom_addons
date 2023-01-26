import time
import json
from datetime import timedelta
from odoo import _, api, fields, models
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
        return Stage.search([("state", "=", "confirm")], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    name = fields.Char(string='Order Reference', required=True,
                       copy=False, readonly=True, default=lambda self: _('New'))

    active = fields.Boolean(default=True)
    color = fields.Integer()
    date = fields.Date()
    time = fields.Datetime()

    company_id = fields.Many2one(comodel_name="res.company", default=lambda self: self.env.company, store=True,
                                 )
    # customer = fields.Many2one(
    #     'res.partner', string='Customer', readonly=False)

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice', string='Practice')

    practice_name = fields.Char(
        string='Practitioner', related='practice_id.name')

    practitioner_id = fields.Many2one(
        comodel_name='podiatry.practitioner', string='Practitioner')

    practitioner_name = fields.Char(
        string='Practitioner', related='practitioner_id.name')

    practitioner_phone = fields.Char(
        string='Phone', related='practitioner_id.phone')

    practitioner_email = fields.Char(
        string='Email', related='practitioner_id.email')

    patient_id = fields.Many2one(
        comodel_name='podiatry.patient', string='Patient')

    patient_name = fields.Char(
        string='Practitioner', related='patient_id.name')

    foot_image1 = fields.Binary(related="patient_id.image1")
    foot_image2 = fields.Binary(related="patient_id.image2")

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
        'podiatry.prescription.line', 'prescription_id', 'Prescription Line')

    product_id = fields.Many2one('product.product', 'Name')

    completed_date = fields.Datetime(string="Completed Date")

    request_date = fields.Date(default=lambda s: fields.Date.today(), compute="_compute_request_date_onchange", store=True, readonly=False,
                               )

    stage_id = fields.Many2one(
        "podiatry.prescription.stage", default=_default_stage, copy=False, group_expand="_group_expand_stage_id")

    state = fields.Selection(related="stage_id.state")

    # state = fields.Selection(
    #     [('Draft', 'Draft'), ('Confirm', 'Confirm')], default='Draft')

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
    def _get_bookout_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        checkout_date = fields.Datetime.context_timestamp(
            self, fields.Datetime.now() + timedelta(days=1)
        )
        return fields.Datetime.to_string(checkout_date)

    # prescription_date = fields.Date(readonly=True)

    prescription_date = fields.Date(
        'Prescription Date', default=fields.Datetime.now())

    close_date = fields.Date(readonly=True)

    bookin_date = fields.Datetime(
        "Book In", required=True, readonly=True, states={"draft": [("readonly", False)]}, default=_get_bookin_date,
    )

    bookout_date = fields.Datetime(
        "Book Out", required=True, readonly=True, states={"draft": [("readonly", False)]}, default=_get_bookout_date,
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

    invoice_done = fields.Boolean('Invoice Done')
    notes = fields.Text('Prescription Note')
    is_invoiced = fields.Boolean(copy=False, default=False)
    is_shipped = fields.Boolean(default=False, copy=False)

    def action_confirm(self):
        self.state = 'confirm'

    def action_draft(self):
        self.state = 'draft'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    diagnosis_client = fields.Text()
    notes_laboratory = fields.Text()
    podiatrist_observation = fields.Text()

    def confirm_request(self):
        for rec in self:
            rec.state = 'confirm'

    def default_examination_chargeable(self):
        settings_examination_chargeable = self.env['ir.config_parameter'].sudo().get_param(
            'examination_chargeable')
        return settings_examination_chargeable

    examination_chargeable = fields.Boolean(
        default=default_examination_chargeable, readonly=1)

    rx_left_only = fields.Boolean()
    rx_right_only = fields.Boolean()
    rx_bilateral_copy = fields.Boolean()
    rx_bilateral_custom = fields.Boolean()

    # RX options
    left_low_profile = fields.Boolean()
    right_low_profile = fields.Boolean()

    shell_foundation = fields.Selection([('cataract_eye', 'Cataract Eye'), ('pterygium', "Pterygium"), ('glaucoma', 'Glaucoma'), ('squint', 'Squint'), ('detachment', 'Detachment'), (
        'laser_myopia', 'laser_myopia'), ('ocular_prosthesis', 'Ocular Prosthesis'), ('chalazion', 'Chalazion'), ('conjunctivitis', 'Conjunctivitis')], string='CIE 10')

    dr_notes = fields.Text('Notes')
    name = fields.Char(required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    podiatric_history = fields.Text()

    @api.onchange('practice_id')
    def onchange_practice_id(self):
        for rec in self:
            return {'domain': {'practitioner_id': [('practice_id', '=', rec.practice_id.id)]}}

    @api.onchange('practitioner_id')
    def onchange_practitioner_id(self):
        for rec in self:
            return {'domain': {'patient_id': [('practitioner_id', '=', rec.practitioner_id.id)]}}

    # @api.onchange('os_sph_distance', 'od_sph_distance')
    # def onchange_sph_distance(self):
    #     if self.os_sph_distance and self.os_sph_distance.isdigit():
    #         self.os_sph_distance = "+" + \
    #             "{:.2f}".format(float(self.os_sph_distance))
    #     elif self.os_sph_distance:
    #         if '-' in self.os_sph_distance:
    #             self.os_sph_distance = "{:.2f}".format(
    #                 float(self.os_sph_distance))
    #     if self.od_sph_distance and self.od_sph_distance.isdigit():
    #         self.od_sph_distance = "+" + \
    #             "{:.2f}".format(float(self.od_sph_distance))
    #     elif self.od_sph_distance:
    #         if '-' in self.od_sph_distance:
    #             self.od_sph_distance = "{:.2f}".format(
    #                 float(self.od_sph_distance))

    # @api.onchange('os_sph_near', 'od_sph_near')
    # def onchange_sph_near(self):
    #     if self.os_sph_near and self.os_sph_near.isdigit():
    #         self.os_sph_near = "+" + "{:.2f}".format(float(self.os_sph_near))
    #     elif self.os_sph_near:
    #         if '-' in self.os_sph_near:
    #             self.os_sph_near = "{:.2f}".format(float(self.os_sph_near))
    #     if self.od_sph_near and self.od_sph_near.isdigit():
    #         self.od_sph_near = "+" + "{:.2f}".format(float(self.od_sph_near))
    #     elif self.od_sph_near:
    #         if '-' in self.od_sph_near:
    #             self.od_sph_near = "{:.2f}".format(float(self.od_sph_near))

    # @api.onchange('od_cyl_distance', 'os_cyl_distance')
    # def onchange_cyl_distance(self):
    #     if self.od_cyl_distance and self.od_cyl_distance.isdigit():
    #         self.od_cyl_distance = "+" + \
    #             "{:.2f}".format(float(self.od_cyl_distance))
    #     elif self.od_cyl_distance:
    #         if '-' in self.od_cyl_distance:
    #             self.od_cyl_distance = "{:.2f}".format(
    #                 float(self.od_cyl_distance))
    #     if self.os_cyl_distance and self.os_cyl_distance.isdigit():
    #         self.os_cyl_distance = "+" + \
    #             "{:.2f}".format(float(self.os_cyl_distance))
    #     elif self.os_cyl_distance:
    #         if '-' in self.os_cyl_distance:
    #             self.os_cyl_distance = "{:.2f}".format(
    #                 float(self.os_cyl_distance))

    # @api.onchange('od_cyl_near', 'os_cyl_near')
    # def onchange_cyl_near(self):
    #     if self.od_cyl_near and self.od_cyl_near.isdigit():
    #         self.od_cyl_near = "+" + "{:.2f}".format(float(self.od_cyl_near))
    #     elif self.od_cyl_near:
    #         if '-' in self.od_cyl_near:
    #             self.od_cyl_near = "{:.2f}".format(float(self.od_cyl_near))
    #     if self.os_cyl_near and self.os_cyl_near.isdigit():
    #         self.os_cyl_near = "+" + "{:.2f}".format(float(self.os_cyl_near))
    #     elif self.os_cyl_near:
    #         if '-' in self.os_cyl_near:
    #             self.os_cyl_near = "{:.2f}".format(float(self.os_cyl_near))

    # @api.onchange('od_add_distance', 'os_add_distance')
    # def onchange_add_distance(self):
    #     if self.od_add_distance and self.od_add_distance.isdigit():
    #         self.od_add_distance = "+" + \
    #             "{:.2f}".format(float(self.od_add_distance))
    #         value = "{:.2f}".format(
    #             float(self.od_sph_distance) + float(self.od_add_distance))
    #         self.od_sph_near = value if '-' in value else "+" + value
    #         self.od_cyl_near = self.od_cyl_distance
    #         self.od_ax_near = self.od_ax_distance
    #     if self.od_add_distance:
    #         if '-' in self.od_add_distance:
    #             self.od_add_distance = "{:.2f}".format(
    #                 float(self.od_add_distance))
    #             value = "{:.2f}".format(
    #                 float(self.od_sph_distance) + float(self.od_add_distance))
    #             self.od_sph_near = value if '-' in value else "+" + value
    #             self.od_cyl_near = self.od_cyl_distance
    #             self.od_ax_near = self.od_ax_distance
    #     if self.os_add_distance and self.os_add_distance.isdigit():
    #         self.os_add_distance = "+" + \
    #             "{:.2f}".format(float(self.os_add_distance))
    #         value = "{:.2f}".format(
    #             float(self.os_sph_distance) + float(self.os_add_distance))
    #         self.os_sph_near = value if '-' in value else "+" + value
    #         self.os_cyl_near = self.os_cyl_distance
    #         self.os_ax_near = self.os_ax_distance
    #     if self.os_add_distance:
    #         if '-' in self.os_add_distance:
    #             self.os_add_distance = "{:.2f}".format(
    #                 float(self.os_add_distance))
    #             value = "{:.2f}".format(
    #                 float(self.os_sph_distance) + float(self.os_add_distance))
    #             self.os_sph_near = value if '-' in value else "+" + value
    #             self.os_cyl_near = self.os_cyl_distance
    #             self.os_ax_near = self.os_ax_distance

    # @api.onchange('od_av_distance', 'os_av_distance')
    # def onchange_av_distance(self):
    #     if self.od_av_distance and self.od_av_distance.isdigit():
    #         self.od_av_distance = "20/" + self.od_av_distance
    #     if self.os_av_distance and self.os_av_distance.isdigit():
    #         self.os_av_distance = "20/" + self.os_av_distance

    ff_varus_rt = fields.Many2one(
        'podiatry.forefoot.value', rel='rx_pod_ff_varus_rt', ondelete='restrict', copy=True)
    ff_varus_lt = fields.Many2one(
        'podiatry.forefoot.value', rel='rx_pod_ff_varus_lt', ondelete='restrict', copy=True)
    ff_valgus_rt = fields.Many2one(
        'podiatry.forefoot.value', rel='rx_pod_ff_valgus_rt', ondelete='restrict', copy=True)
    ff_valgus_lt = fields.Many2one(
        'podiatry.forefoot.value', rel='rx_pod_ff_valgus_lt', ondelete='restrict', copy=True)

    # def get_podiatry_prescription_template_id(self):
    #     self.ensure_one()
    #     report_name = 'report_podiatry_prescription'
    #     template_obj = self.env['report.custom.template']

    #     template = template_obj.sudo().get_template(report_name)

    #     if not template: template_obj.reset_template(report_name=report_name)
    #     template = template_obj.sudo().get_template(report_name)
    #     return template

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
                'context': {'default_prescription_id': self.id, 'default_partner_id': self.practitioner_id.id},
                'type': 'ir.actions.act_window',
            }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'podiatry.prescription') or _('New')
        res = super(Prescription, self).create(vals)
        if res.stage_id.state in ("draft", "close"):
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


class ReportCustomTemplate(models.Model):
    _inherit = 'report.custom.template'

    def get_report_list(self):
        res = super(ReportCustomTemplate, self).get_report_list()

        res["report_podiatry_prescription"] = {

            'name_display': 'Podiatry Prescription Template',
            'template': 'pink',
            'paperformat_id': self.env.ref("podiatry.paperformat_podiatry_prescription").id,
            'visible_watermark': True,
            'lines': [
                {'name': 'Header Section',
                 'name_technical': 'section_header',
                 'model_id': 'res.company',
                 'type': 'address',
                 'color': ' #daa6a6',
                 'preview_img': '1_top.png',
                 'address_field_ids': [
                     (0, 0, {'prefix': False, 'sequence': 10,
                      'field_id': 'street', }),
                     (0, 0, {'prefix': 'next_line',
                      'sequence': 20, 'field_id': 'street2', }),
                     (0, 0, {'prefix': 'next_line',
                      'sequence': 30, 'field_id': 'city', }),
                     (0, 0, {'prefix': 'comma', 'sequence': 40,
                      'field_id': 'state_id', 'field_display_field_id': 'name', }),
                     (0, 0, {'prefix': 'comma',
                      'sequence': 50, 'field_id': 'zip', }),
                     (0, 0, {'prefix': 'next_line', 'sequence': 60,
                      'field_id': 'country_id', 'field_display_field_id': 'name', }),
                 ],
                 },

                {'name': 'Patient Address',
                 'name_technical': 'section_partner_address',
                 'model_id': 'podiatry.patient',
                 'type': 'address',
                 'color': ' #bfb781',
                 'preview_img': '2_left.png',
                 'address_field_ids': [
                     (0, 0, {'prefix': False, 'sequence': 10,
                      'field_id': 'street', }),
                     (0, 0, {'prefix': 'next_line',
                      'sequence': 20, 'field_id': 'street2', }),
                     (0, 0, {'prefix': 'next_line',
                      'sequence': 30, 'field_id': 'city', }),
                     (0, 0, {'prefix': 'comma', 'sequence': 40,
                      'field_id': 'state_id', 'field_display_field_id': 'name'}),
                     (0, 0, {'prefix': 'comma',
                      'sequence': 50, 'field_id': 'zip', }),
                     (0, 0, {'prefix': 'next_line', 'sequence': 60,
                      'field_id': 'country_id', 'field_display_field_id': 'name'}),
                 ],
                 },

                {'name': 'Other Fields',
                 'name_technical': 'section_other_fields',
                 'model_id': 'sale.order',
                 'type': 'fields',
                 'color': '#81bcbf',
                 'preview_img': '2_right.png',
                 'field_ids': [
                     (0, 0, {'sequence': 10, 'field_id': 'practitioner_id',
                      'label': 'Practitioner'}),
                     (0, 0, {'sequence': 20, 'field_id': 'client_order_ref',
                      'label': 'Your Reference'}),
                     (0, 0, {'sequence': 30, 'field_id': 'date_order',
                      'label': 'Quotation Date'}),
                     (0, 0, {'sequence': 40, 'field_id': 'validity_date',
                      'label': 'Expiration'}),
                     (0, 0, {'sequence': 50, 'field_id': 'user_id',
                      'label': 'Salesperson'}),
                 ],
                 },

                {'name': 'Lines Section',
                 'name_technical': 'section_lines',
                 'model_id': 'sale.order.line',
                 'type': 'lines',
                 'color': '#9095c7',
                 'preview_img': '3_lines.png',
                 'data_field_names': 'display_type',
                 'line_field_ids': [
                     (0, 0, {'sequence': 10, 'alignment': 'left',
                      'field_id': 'name', 'label': 'Description'}),
                     (0, 0, {'sequence': 20, 'alignment': 'center',
                      'field_id': 'product_uom_qty', 'label': 'Quantity'}),
                     (0, 0, {'sequence': 30, 'alignment': 'right',
                      'field_id': 'price_unit', 'label': 'Unit Price'}),
                     (0, 0, {'sequence': 40, 'alignment': 'center',
                      'field_id': 'product_uom', 'label': 'UOM'}),
                     (0, 0, {'sequence': 50, 'alignment': 'right', 'field_id': 'discount',
                      'label': 'Disc.%', 'null_hide_column': True}),
                     (0, 0, {'sequence': 60, 'alignment': 'center',
                      'field_id': 'tax_id', 'label': 'Taxes'}),
                     (0, 0, {'sequence': 70, 'alignment': 'right', 'field_id': 'price_subtotal', 'label': 'Amount',
                      'currency_field_name': 'order_id.currency_id', 'thousands_separator': 'applicable'}),
                 ],
                 },

                {'name': 'Bottom Amount Section',
                 'name_technical': 'section_bottom_amount',
                 'model_id': 'sale.order',
                 'type': 'fields',
                 'color': '#81bcbf',
                 'preview_img': '4_bottom_right.png',
                 'field_ids': [
                     (0, 0, {'sequence': 10, 'thousands_separator': 'applicable',
                      'field_id': 'amount_untaxed', 'label': 'Untaxed Amount'}),
                     (0, 0, {'sequence': 20, 'thousands_separator': 'applicable',
                      'field_id': 'amount_tax', 'label': 'Tax'}),
                     (0, 0, {'sequence': 30, 'thousands_separator': 'applicable',
                      'field_id': 'amount_total', 'label': 'Amount With Tax'}),
                 ],
                 },

                {'name': 'Footer Section',
                 'name_technical': 'section_footer',
                 'model_id': 'res.company',
                 'type': 'address',
                 'color': ' #dcaf95',
                 'preview_img': '5_bottom.png',
                 'address_field_ids': [
                     (0, 0, {'label': 'Phone',
                      'sequence': 10, 'field_id': 'phone'}),
                     (0, 0, {'label': 'Email',
                      'sequence': 20, 'field_id': 'email'}),
                     (0, 0, {'label': 'Web', 'sequence': 30,
                      'field_id': 'website'}),
                     (0, 0, {'label': 'Tax ID',
                      'sequence': 40, 'field_id': 'vat'}),
                 ],
                 },

                {'name': 'Other Options',
                 'name_technical': 'section_other_options',
                 'type': 'options',
                 'color': ' #93c193',
                 'preview_img': 'other.png',
                 'option_field_ids': [
                     (0, 0, {'field_type': 'char', 'name_technical': 'state_order',
                      'name': 'HEADING:IF STATE IS DRAFT/SENT', 'value_char': 'PRESCRIPTION'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'state_quotation',
                      'name': 'HEADING:IF STATE IS NOT DRAFT/SENT', 'value_char': 'PRESCRIPTION'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'heading_device_details',
                      'name': 'HEADING:DEVICE DETAILS SECTION', 'value_char': 'PRESCRIPTION'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'heading_orderline_details',
                      'name': 'HEADING:ORDER LINE DETAILS', 'value_char': 'PRODUCTS / SERVICES'}),
                     (0, 0, {'field_type': 'combo_box', 'name_technical': 'header_section_sequence', 'key_combo_box': 'report_utils2__header_section_sequence',
                      'name': 'Order of Header Section', 'value_combo_box': 'address_logo_reference', }),
                     (0, 0, {'field_type': 'break',
                      'name_technical': '-1', 'name': '-', }),

                     (0, 0, {'field_type': 'char', 'name_technical': 'label_customer',
                      'name': 'LABEL: Patient', 'value_char': 'PATIENT'}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_shipping_address',
                      'name': 'Show shipping address', 'value_boolean': False}),
                     (0, 0, {'field_type': 'break',
                      'name_technical': '-1', 'name': '-', }),

                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_serial_number',
                      'name': 'Show serial number ?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'serial_number_heading',
                      'name': 'Serial number heading', 'value_char': 'Sl.'}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_product_image',
                      'name': 'Show product image ?', 'value_boolean': False}),
                     (0, 0, {'field_type': 'integer', 'name_technical': 'product_image_position',
                      'name': 'Product image position (Column)', 'value_integer': 2}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'product_image_column_heading',
                      'name': 'Product image heading', 'value_char': 'Product Image'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'product_image_width',
                      'name': 'Product image width', 'value_char': '75px'}),
                     (0, 0, {'field_type': 'break',
                      'name_technical': '-1', 'name': '-', }),

                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_amount_in_text',
                      'name': 'Show Amount in Words ?', 'value_boolean': False}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'label_amount_in_text',
                      'name': 'Label Amount in Words', 'value_char': 'Amount In Text'}),
                     (0, 0, {'field_type': 'break',
                      'name_technical': '-1', 'name': '-', }),

                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_note',
                      'name': 'Show Terms & Conditions ?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_payment_term_note',
                      'name': 'Show Payment Terms Remark ?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_fiscal_position_note',
                      'name': 'Show Fiscal Position Remark ?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_company_tagline_footer',
                      'name': 'Show Company tagline Footer ?', 'value_boolean': True}),

                 ],
                 },
            ],
        }

        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
