# -*- coding: utf8 -*-
import dateutil.utils
import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

# from . import podiatry_practice

# from lxml import etree
# added import statement in try-except because when server runs on
# windows operating system issue arise because this library is not in Windows.
try:
    from odoo.tools import image_colorize
except:
    image_colorize = False


class Doctor(models.Model):

    _name = "podiatry.doctor"
    _description = "Doctor"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }
    _rec_name = 'doctor_id'

    name = fields.Char(string="First Name", required=True, tracking=True)
    surname = fields.Char(string="Last Name", required=True, tracking=True)
    doctor_tc = fields.Char(string="TC NO", required=True)

    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Contact",
    )

    doctor_id = fields.Many2many('res.partner', domain=[(
        'is_doctor', '=', True)], string="Doctor", required=True)

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string='Practice', required=True)

    prescription_id = fields.One2many(
        comodel_name='podiatry.prescription',
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
    reference = fields.Char(string='Doctor Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))

    brans_kod = fields.Char(string="Branch Code", required=True)
    sertifika_kod = fields.Selection([
        ('0', 'Yok'),
        ('56', 'Hemodiyaliz'),
        ('109', 'Aile Hekimliği')
    ], string="Sertifika Kod")
    birth = fields.Date(string="Date of Birth",
                        date_format="dd.MM.yyyy")
    age = fields.Integer(string="Age", compute='_compute_age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], default='other', tracking=True)
    active = fields.Boolean(string='Active', default='True', tracking=True)
    image = fields.Image(string="Image")
    notes = fields.Text(string="Notes")

    @api.depends('birth')
    def _compute_age(self):
        for rec in self:
            today = dateutil.utils.today()
            if rec.birth:
                rec.age = today.year - rec.birth.year
            else:
                rec.age = 0

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['podiatry.prescription'].search_count(
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

    other_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='podiatry_doctor_partners_rel',
        column1='doctor_id', column2='partner_id',
        string="Other Contacts",
    )

    same_reference_doctor_id = fields.Many2one(
        comodel_name='podiatry.doctor',
        string='Doctor with same Identity',
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
            'podiatry', 'static/img', 'avatar.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _add_followers(self):
        for doctor in self:
            partner_ids = (doctor.user_id.partner_id |
                           doctor.responsible_id.partner_id).ids
            doctor.message_subscribe(partner_ids=partner_ids)

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model
    def create(self, vals):
        if not vals.get('notes'):
            vals['notes'] = 'New Doctor'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'podiatry.doctor') or _('New')
        doctor = super(Doctor, self).create(vals)
        doctor._add_followers()
        return doctor

    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         name = '[' + rec.reference + '] ' + rec.name
    #         result.append((rec.id, name))
    #     return result

    def name_get(self):
        result = []
        for rec in self:
            name = rec.doctor_tc + ' : ' + rec.name + ' ' + rec.surname
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(Doctor, self).write(values)
        if 'user_id' in values or 'other_partner_ids' in values:
            self._add_followers()
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate Doctor.'))

    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'podiatry.prescription',
            'domain': [('doctor_id', '=', self.id)],
            'context': {'default_doctor_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }

    # def action_open_prescriptions(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Prescriptions',
    #         'res_model': 'podiatry.prescription',
    #         'domain': [('doctor_id', '=', self.id)],
    #         'context': {'default_doctor_id': self.id},
    #         'view_mode': 'kanban,tree,form',
    #         'target': 'current',
    #     }
