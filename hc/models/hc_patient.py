import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource


class Patient(models.Model):
    _name = 'hc.patient'
    _description = "Patient"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    @api.model
    def _get_sequence_code(self):
        return 'hc.patient'

    active = fields.Boolean(string="Active", default=True, tracking=True)
    name = fields.Char(string="Patient Name", index=True)
    color = fields.Integer(string="Color Index (0-15)")

    number = fields.Char(string="Patient Number")

    identification = fields.Char(string="Identification", index=True)

    birthdate = fields.Datetime(string="Birthdate")

    email = fields.Char(string="E-mail")
    phone = fields.Char(string="Telephone")
    mobile = fields.Char(string="Mobile")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    country_id = fields.Many2one(
        comodel_name='res.country', string="Country",
        default=lambda self: self.env.company.country_id,
    )
    state_id = fields.Many2one(
        comodel_name='res.country.state', string="State",
        default=lambda self: self.env.company.state_id,
    )
    city = fields.Char(string="City")
    zip = fields.Char(string="ZIP Code")

    notes = fields.Text(string="Notes")

    sex = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string="Sex")
    blood = fields.Selection(selection=[
        ('o-', 'O-'), ('o+', 'O+'),
        ('a-', 'A-'), ('a+', 'A+'),
        ('b-', 'B-'), ('b+', 'B+'),
        ('ab-', 'AB-'), ('ab+', 'AB+'),
        ('other', 'Other'),
    ], string="Blood Group")

    signature = fields.Binary(string="Signature")

    birth_country_id = fields.Many2one(
        comodel_name='res.country', string="Country of Birth",
        default=lambda self: self.env.company.country_id,
    )
    birth_state_id = fields.Many2one(
        comodel_name='res.country.state', string="Birthplace",
        default=lambda self: self.env.company.state_id,
        domain="[('country_id', '=', birth_country_id)]",
    )
    nationality_id = fields.Many2one(
        comodel_name='res.country', string="Nationality",
        default=lambda self: self.env.company.country_id,
    )

    civil_status_id = fields.Many2one(
        comodel_name='hc.patient.civil_status',
        string="Civil Status",
    )
    education_id = fields.Many2one(
        comodel_name='hc.patient.education',
        string="Education",
    )
    occupation_id = fields.Many2one(
        comodel_name='hc.patient.occupation',
        string="Occupation",
    )
    user_id = fields.Many2one(
        comodel_name='res.users', string="User",
    )
    responsible_id = fields.Many2one(
        comodel_name='res.users', string="Responsible",
        default=lambda self: self.env.user,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Contact",
    )

    other_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='hc_patient_partners_rel',
        column1='patient_id', column2='partner_id',
        string="Other Contacts",
    )

    age = fields.Char(compute='_compute_age')

    @api.model
    def _relativedelta_to_text(self, delta):
        result = []

        if delta:
            if delta.years > 0:
                result.append(
                    "{years} {unit}".format(
                        years=delta.years,
                        unit=_("year") if delta.years == 1 else _("years"),
                    )
                )
            if delta.months > 0 and delta.years < 9:
                result.append(
                    "{months} {unit}".format(
                        months=delta.months,
                        unit=_("month") if delta.months == 1 else _("months"),
                    )
                )
            if delta.days > 0 and not delta.years:
                result.append(
                    "{days} {unit}".format(
                        days=delta.days,
                        unit=_("day") if delta.days == 1 else _("days"),
                    )
                )

        return bool(result) and " ".join(result)

    @api.depends('birthdate')
    def _compute_age(self):
        now = fields.Datetime.now()
        for patient in self:
            delta = relativedelta(now, patient.birthdate)
            patient.age = self._relativedelta_to_text(delta)

        return

    same_identification_patient_id = fields.Many2one(
        comodel_name='hc.patient',
        string='Patient with same Identity',
        compute='_compute_same_identification_patient_id',
    )

    @api.depends('identification')
    def _compute_same_identification_patient_id(self):
        for patient in self:
            domain = [
                ('identification', '=', patient.identification),
            ]

            origin_id = patient._origin.id

            if origin_id:
                domain += [('id', '!=', origin_id)]

            patient.same_identification_patient_id = bool(patient.identification) and \
                self.with_context(active_test=False).sudo().search(domain, limit=1)

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hc', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _add_followers(self):
        for patient in self:
            partner_ids = (patient.user_id.partner_id | patient.responsible_id.partner_id).ids
            patient.message_subscribe(partner_ids=partner_ids)

    def _set_number(self):
        for patient in self:
            sequence = self._get_sequence_code()
            patient.number = self.env['ir.sequence'].next_by_code(sequence)
        return

    @api.model
    def create(self, values):
        patient = super(Patient, self).create(values)
        patient._add_followers()
        patient._set_number()

        return patient

    def write(self, values):
        result = super(Patient, self).write(values)
        if 'user_id' in values or 'other_partner_ids' in values:
            self._add_followers()
        return result
