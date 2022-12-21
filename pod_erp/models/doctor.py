import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError

# from lxml import etree
# added import statement in try-except because when server runs on
# windows operating system issue arise because this library is not in Windows.
try:
    from odoo.tools import image_colorize
except:
    image_colorize = False


class Doctor(models.Model):
    _name = 'pod.doctor'
    _inherit = ['mail.thread',
                'mail.activity.mixin', 'image.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }
    # _inherit = "res.partner"
    _description = 'doctor'

    _rec_name = 'doctor_id'

    create_users_button = fields.Boolean()
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Doctor')

    patient_ids = fields.One2many(
        comodel_name='pod.patient',
        inverse_name='primary_doctor_id',
        string='Patients'
    )

    practice_id = fields.Many2one(
        comodel_name='pod.practice',
        inverse_name='doctor_ids',
        string='Practice')

    doctor_id = fields.Many2many('res.partner', domain=[(
        'is_doctor', '=', True)], string="doctor", required=True)

    @api.model
    def _default_image(self):
        '''Method to get default Image'''
        image_path = get_module_resource('hr', 'static/src/img',
                                         'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    active = fields.Boolean(string="Active", default=True, tracking=True)
    # name = fields.Char(string="Practitioner Name", index=True, required=True)
    color = fields.Integer(string="Color Index (0-15)")
    code = fields.Char(string="Code", copy=False)
    active = fields.Boolean(string="Active", default=True, tracking=True)
    identification = fields.Char(string="Identification", index=True)
    reference = fields.Char(string='Practitioner Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    email = fields.Char(string="E-mail")
    phone = fields.Char(string="Telephone")
    mobile = fields.Char(string="Mobile")
    practice_address_id = fields.Many2one('res.partner', string="Address", )
    street = fields.Char(related='doctor_id.street', readonly=False)
    street2 = fields.Char(related='doctor_id.street2', readonly=False)
    zip_code = fields.Char(related='doctor_id.zip', readonly=False)
    city = fields.Char(related='doctor_id.city', readonly=False)
    zip = fields.Char(string="ZIP Code")
    state_id = fields.Many2one(
        "res.country.state", related='doctor_id.state_id', readonly=False)
    country_id = fields.Many2one(
        'res.country', related='doctor_id.country_id', readonly=False)

    notes = fields.Text(string="Notes")

    salutation = fields.Selection(selection=[
        ('doctor', 'Practitioner'),
        ('mr', 'Mr.'),
        ('ms', 'Ms.'),
        ('mrs', 'Mrs.'),
    ], string="Salutation")

    signature = fields.Binary(string="Signature")

    related_user_id = fields.Many2one(related='partner_id.user_id')
    prescription_count = fields.Integer(compute='get_prescription_count')

    @api.model
    def _get_sequence_code(self):
        return 'pod.doctor'

    sequence = fields.Integer(
        string="Sequence", required=True,
        default=5,
    )

    def open_doctor_prescriptions(self):
        for records in self:
            return {
                'name': _('Doctor Prescription'),
                'view_type': 'form',
                'domain': [('doctor', '=', records.id)],
                'res_model': 'doctor.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_doctor': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['doctor.prescription'].search_count(
                [('doctor', '=', records.id)])
            records.prescription_count = count

    prescription_date = fields.Datetime(
        'Prescription Date', default=fields.Datetime.now)

    same_reference_doctor_id = fields.Many2one(
        comodel_name='pod.doctor',
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
            'pod_erp', 'static/src/description', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _add_followers(self):
        for doctor in self:
            partner_ids = (doctor.user_id.partner_id |
                           doctor.responsible_id.partner_id).ids
            doctor.message_subscribe(partner_ids=partner_ids)

    def _set_code(self):
        for doctor in self:
            sequence = self._get_sequence_code()
            doctor.code = self.env['ir.sequence'].next_by_code(
                sequence)
        return

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model
    def create_doctor(self, vals):
        if not vals.get('notes'):
            vals['notes'] = 'New Practitioner'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'pod.doctor') or _('New')
        doctor = super(Doctor, self).create(vals)
        doctor._set_code()
        return doctor
    # def create_doctors(self, vals):
    #     print('.....res')
    #     self.is_doctor = True
    #     if not vals.get('notes'):
    #         vals['notes'] = 'New Practitioner'
    #     if vals.get('reference', _('New')) == _('New'):
    #         vals['reference'] = self.env['ir.sequence'].next_by_code(
    #             'pod.doctor') or _('New')
    #     if len(self.partner_id.user_ids):
    #         raise UserError(_('User for this doctor already created.'))
    #     else:
    #         self.create_users_button = False
    #     doctor_id = super(Doctor, self).create(vals)
    #     doctor_id.append(self.env['res.groups'].search(
    #         [('name', '=', 'Doctors')]).id)
    #     doctor_id.append(self.env['res.groups'].search(
    #         [('name', '=', 'Internal User')]).id)
    #     doctor_id._set_code()
    #     doctor_id._add_followers()

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Name ',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref("doctor.view_create_user_wizard_form").id,
    #         'target': 'new',
    #         'res_model': 'res.users',
    #         'context': {'default_partner_id': self.partner_id.id, 'default_is_doctor': True,
    #                     'default_groups_id': [(6, 0, doctor_id)]}
    #     }

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.reference + '] ' + rec.name
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(Doctor, self).write(values)
        if 'user_id' in values:
            self._add_followers()
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate Doctor.'))

    def open_doctor_prescriptions(self):
        for records in self:
            return {
                'name': _('Doctor Prescription'),
                'view_type': 'form',
                'domain': [('doctor', '=', records.id)],
                'res_model': 'doctor.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_doctor': self.id},
                'type': 'ir.actions.act_window',
            }
