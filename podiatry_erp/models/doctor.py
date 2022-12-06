import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

from . import practice

# from lxml import etree
# added import statement in try-except because when server runs on
# windows operating system issue arise because this library is not in Windows.
try:
    from odoo.tools import image_colorize
except:
    image_colorize = False


class Doctor(models.Model):
    _name = 'podiatry.doctor'
    _inherit = ['mail.thread',
                'mail.activity.mixin', 'image.mixin']

    _inherits = {
        'res.partner': 'partner_id',
    }

    _rec_name = 'doctor_id'

    _description = 'doctor'

    patient_ids = fields.One2many(
        comodel_name='podiatry.patient',
        inverse_name='doctor_id',
        string='Patients'
    )

    doctor_id = fields.Many2many('res.partner', domain=[(
        'is_practitioner', '=', True)], string="doctor", required=True)

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string='Practice')

    prescription_id = fields.One2many(
        comodel_name='medical.prescription',
        inverse_name='doctor_id',
        string='Prescriptions')

    @api.model
    def _default_image(self):
        '''Method to get default Image'''
        image_path = get_module_resource('hr', 'static/src/img',
                                         'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    active = fields.Boolean(string="Active", default=True, tracking=True)
    # name = fields.Char(string="Name", index=True)
    color = fields.Integer(string="Color Index (0-15)")
    code = fields.Char(string="Code", copy=False)
    reference = fields.Char(string='Practitioner Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))

    email = fields.Char(string="E-mail")
    phone = fields.Char(string="Telephone")
    mobile = fields.Char(string="Mobile")

    notes = fields.Text(string="Notes")

    salutation = fields.Selection(selection=[
        ('doctor', 'Practitioner'),
        ('mr', 'Mr.'),
        ('ms', 'Ms.'),
        ('mrs', 'Mrs.'),
    ], string="Salutation")

    signature = fields.Binary(string="Signature")

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')

    prescription_id = fields.One2many(
        comodel_name='medical.prescription',
        inverse_name='doctor_id',
        string="Prescriptions",
    )

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['medical.prescription'].search_count(
                [('doctor_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    prescription_date = fields.Datetime(
        'Prescription Date', default=fields.Datetime.now)

    user_id = fields.Many2one(
        comodel_name='res.users', string="User",
    )

    responsible_id = fields.Many2one(
        comodel_name='res.users', string="Created By",
        default=lambda self: self.env.user,
    )

    @api.onchange('doctor_id')
    def _onchange_doctor(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.doctor_id
        self.doctor_address_id = address_id

    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='restrict',
                                 help='Partner-related data')

    doctor_address_id = fields.Many2one(
        'res.partner', string="Address", )

    other_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='podiatry_doctor_partners_rel',
        column1='doctor_id', column2='partner_id',
        string="Other Contacts",
    )

    @api.model
    def _relativedelta_to_text(self, delta):
        result = []

        if delta:
            if delta.years > 0:
                result.append(
                    "{years} {doctor}".format(
                        years=delta.years,
                        doctor=_(
                            "year") if delta.years == 1 else _("years"),
                    )
                )
            if delta.months > 0 and delta.years < 9:
                result.append(
                    "{months} {doctor}".format(
                        months=delta.months,
                        doctor=_("month") if delta.months == 1 else _(
                            "months"),
                    )
                )
            if delta.days > 0 and not delta.years:
                result.append(
                    "{days} {doctor}".format(
                        days=delta.days,
                        doctor=_(
                            "day") if delta.days == 1 else _("days"),
                    )
                )

        return bool(result) and " ".join(result)

    same_reference_doctor_id = fields.Many2one(
        comodel_name='podiatry.doctor',
        string='Practitioner with same Identity',
        compute='_compute_same_reference_doctor_id',
    )

    @api.depends('reference')
    def _compute_same_reference_doctor_id(self):
        for doctor in self:
            domain = [
                ('reference', '=', doctor.reference),
            ]

            origin_id = doctor._origin.id

            if origin_id:
                domain += [('id', '!=', origin_id)]

            doctor.same_reference_doctor_id = bool(doctor.reference) and \
                self.with_context(active_test=False).sudo().search(
                    domain, limit=1)

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'podiatry_erp', 'static/src/description', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _add_followers(self):
        for doctor in self:
            partner_ids = (doctor.user_id.partner_id |
                           doctor.responsible_id.partner_id).ids
            doctor.message_subscribe(partner_ids=partner_ids)

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    # @api.model
    # def create_doctors(self, vals):
    #     if not vals.get('notes'):
    #         vals['notes'] = 'New Practitioner'
    #     if vals.get('reference', _('New')) == _('New'):
    #         vals['reference'] = self.env['ir.sequence'].next_by_code(
    #             'podiatry.doctor') or _('New')
    #     doctor = super(Doctor, self).create(vals)
    #     doctor._add_followers()
    #     return doctor

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'podiatry.doctor') or _('New')
        res = super(Doctor, self).create(vals)
        return res

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.reference + '] ' + rec.name
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(Doctor, self).write(values)
        if 'user_id' in values or 'other_partner_ids' in values:
            self._add_followers()
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate doctor.'))

    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'medical.prescription',
            'domain': [('doctor_id', '=', self.id)],
            'context': {'default_doctor_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
