from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import re


class PodiatryDoctor(models.Model):
    _name = 'pod.doctor'
    _description = 'Podiatry Doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}

    create_users_button = fields.Boolean()
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Doctor')
    is_practitioner = fields.Boolean(default=False)
    practitioner_role_ids = fields.Many2many(
        string="Practitioner Roles", comodel_name="podiatry.role"
    )  # Field: PractitionerRole/role

    # doctor_name = fields.Char(string='Doctor Name',
    #                           required=True, tracking=True)
    address = fields.Char(string='Address', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], default='male')
    phone = fields.Char(string='Phone', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)
    # department_id = fields.Many2one(
    #     "hr.department", string='Department', required=True, tracking=True)
    view_prescription_ids = fields.One2many('pod.prescription', 'appointed_doctor_id', string="prescription Count",
                                            readonly=True)
    age = fields.Integer(string='Age', required=True, tracking=True)
    # status = fields.Selection([('fulltime', 'Full time'),('parttime', 'Part time')], required=True, default='fulltime', tracking=True)
    description = fields.Text()
    enrolled_date = fields.Date(string='Enrolled Date', tracking=True)
    image = fields.Binary(string='Image', attachment=True)
    total_prescriptions = fields.Integer(
        string='Total prescriptions', compute='_compute_prescriptions')

    active = fields.Boolean(string="Active", default=True)

    # def action_status_halftime(self):
    #     self.status = 'parttime'

    # def action_status_fulltime(self):
    #     self.status = 'fulltime'

    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (Copy)", self.name)
        default['note'] = "Copied Record"
        return super(PodiatryDoctor, self).copy(default)

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            valid_email = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                                   record.email)

            if valid_email is None:
                raise ValidationError('Please provide a valid E-mail')

    @api.constrains('age')
    def _check_doctor_age(self):
        for record in self:
            if record.age <= 0:
                raise ValidationError('Age must be greater than 0')

    # same as view_prescription_ids but implemented using computed fields
    # compute prescriptions of individual doctor
    def _compute_prescriptions(self):
        for record in self:
            record.total_prescriptions = self.env['pod.prescription'].search_count(
                [('appointed_doctor_id', '=', record.id)])

    def create_doctors(self):
        print('.....res')
        self.is_doctor = True
        if len(self.partner_id.user_ids):
            raise UserError(_('User already created.'))
        else:
            self.create_users_button = False
        doctor_id = []
        doctor_id.append(self.env['res.groups'].search(
            [('name', '=', 'Doctors')]).id)
        doctor_id.append(self.env['res.groups'].search(
            [('name', '=', 'Internal User')]).id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Name ',
            'view_mode': 'form',
            'view_id': self.env.ref("doctor.view_create_user_wizard_form").id,
            'target': 'new',
            'res_model': 'res.users',
            'context': {'default_partner_id': self.partner_id.id, 'default_is_doctor': True,
                        'default_groups_id': [(6, 0, doctor_id)]}
        }

    # def action_url(self):
    #     return {
    #         "type": "ir.actions.act_url",
    #         "url": "https://nwpodiatric.com",
    #         "target": "new",
    #     }
