from datetime import date, datetime
from odoo import _, api, fields, models
from odoo.modules import get_module_resource
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class PodiatryPatient(models.Model):
    _name = 'pod.patient'
    _description = 'Podiatry Patient'
    _order = 'id desc'
    _inherit = ['pod.abstract.entity', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Patient Name', required=True, tracking=True)
    identification_code = fields.Char(
        string='Internal ID',
        help='Patient Identification',
    )
    general_info = fields.Text(
        string='Información General',
    )
    address = fields.Char(string='Address', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], default="male", tracking=True)
    phone = fields.Char(string='Phone', required=True, tracking=True)
    age = fields.Integer(string='Age', required=True, tracking=True)
    email = fields.Char(string='Email', tracking=True)
    patient_prescription_ids = fields.One2many('pod.prescription', 'patient_id', string="prescription Count",
                                               readonly=True)

    primary_doctor_id = fields.Many2one('pod.doctor', string="Primary Doctor")
    total_prescriptions = fields.Integer(
        string='No. of prescriptions', compute='_compute_prescriptions')

    # check if the patient is already exists based on the patient name and phone number
    @api.constrains('name', 'phone')
    def _check_patient_exists(self):
        for record in self:
            patient = self.env['pod.patient'].search(
                [('name', '=', record.name), ('phone', '=', record.phone), ('id', '!=', record.id)])
            if patient:
                raise ValidationError(f'Patient {record.name} already exists')

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            valid_email = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                                   record.email)
            if valid_email is None:
                raise ValidationError('Please provide a valid Email')

    @api.constrains('age')
    def _check_patient_age(self):
        for record in self:
            if record.age <= 0:
                raise ValidationError('Age must be greater than 0')

    # compute prescriptions of individual patient
    def _compute_prescriptions(self):
        for record in self:
            record.total_prescriptions = self.env['pod.prescription'].search_count(
                [('patient_id', '=', record.id)])

    def action_url(self):
        return {
            "type": "ir.actions.act_url",
            "url": "https://nwpodiatric.com",
            "target": "new",
        }

    @api.model
    def _create_vals(self, vals):
        vals = super(PodiatryPatient, self)._create_vals(vals)
        if not vals.get('identification_code'):
            Seq = self.env['ir.sequence']
            vals['identification_code'] = Seq.sudo().next_by_code(
                self._name,
            )
        # vals.update({
        #     'customer': True,
        # })
        return vals

    def _get_default_image_path(self, vals):
        super(PodiatryPatient, self)._get_default_image_path(vals)
        return get_module_resource(
            'medical', 'static/src/img', 'patient-avatar.png'
        )
