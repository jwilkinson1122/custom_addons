import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource


class Patient(models.Model):
    _name = 'patient_clinic.patient'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _rec_name = 'rec_name'

    # patient_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
    #                          index=True, default=lambda self: _('New'))
    name = fields.Char(string='Name', required=True)
    rec_name = fields.Char(string='Recname',
                           compute='_compute_fields_rec_name')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default='male', string="Gender", required=True)
    age = fields.Char(string='Age')
    image = fields.Binary(string='Image')
    description = fields.Text(string='Description')

    user_id = fields.Many2one(
        comodel_name='res.users', string="User",
    )
    responsible_id = fields.Many2one(
        comodel_name='res.users', string="Created By",
        default=lambda self: self.env.user,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Contact",
    )

    # Owner
    owner = fields.Many2one(
        'patient_clinic.doctor', string='Owner', store=True, readonly=False)
    owner_id = fields.Integer(
        related='owner.id', string='Patient Owner ID')
    owner_name = fields.Char(
        related='owner.name', string='Owner Name')

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
        comodel_name='patient_clinic.patient',
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
                self.with_context(active_test=False).sudo().search(
                    domain, limit=1)

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'patient_clinic', 'static/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _add_followers(self):
        for patient in self:
            partner_ids = (patient.user_id.partner_id |
                           patient.responsible_id.partner_id).ids
            patient.message_subscribe(partner_ids=partner_ids)

    # def _set_number(self):
    #     for patient in self:
    #         sequence = self._get_sequence_code()
    #         patient.number = self.env['ir.sequence'].next_by_code(sequence)
    #     return

    # @api.model
    # def create(self, vals):
    #     if vals.get('patient_id', _('New')) == _('New'):
    #         vals['patient_id'] = self.env['ir.sequence'].next_by_code(
    #             'patient.seq') or _('New')
    #     result = super(Patient, self).create(vals)
    #     return result

    def _set_number(self, vals):
        if vals.get('patient_id', _('New')) == _('New'):
            vals['patient_id'] = self.env['ir.sequence'].next_by_code(
                'patient.seq') or _('New')
        result = super(Patient, self).create(vals)
        return result

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

    # Prescription
    prescription_count = fields.Integer(compute='compute_prescription_count')

    # Button Patient Handle
    def open_patient_prescription(self):
        return {
            'name': _('Prescriptions'),
            'domain': [('patient', '=', self.id)],
            'view_type': 'form',
            'res_model': 'patient_clinic.prescription',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }
    # Button Patient Count

    def compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['patient_clinic.prescription'].search_count(
                [('patient', '=', self.id)])
