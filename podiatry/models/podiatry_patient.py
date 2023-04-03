import base64
from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class Patient(models.Model):
    _name = 'podiatry.patient'
    _description = "Patient"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }
    # _rec_name = 'patient_id'
    
    patient_id = fields.Many2one('res.partner',domain=[('is_patient','=',True)],string="Patient")

    active = fields.Boolean(string="Active", default=True, tracking=True)
    # name = fields.Char(string="Patient Name", index=True)
    color = fields.Integer(string="Color Index (0-15)")

    code = fields.Char(string="Code", copy=False)

    identification = fields.Char(string="Identification", index=True)

    reference = fields.Char(string='Patient Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))

    
    birthdate = fields.Date(string="Date of Birth")

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

    gender = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string="Gender")

    diagnosis = fields.Selection(selection=[
        ('plantar_fasciitis', 'Plantar Fasciitis'),
        ('diabetes', 'Diabetes'),
        ('other', 'Other'),
    ], string="Diagnosis")

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

    diagnosis_id = fields.Many2one(
        comodel_name='podiatry.patient.diagnosis',
        string="Diagnosis",
    )

    user_id = fields.Many2one(
        comodel_name='res.users', string="User",
    )

    responsible_id = fields.Many2one(
        comodel_name='res.users', string="Created By",
        default=lambda self: self.env.user,
    )

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        required=True,
        string="Practice",
    )

    practitioner_id = fields.Many2one(
        comodel_name='podiatry.practitioner',
        required=True,
        string='Practitioner')

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')

    patient_prescription_ids = fields.One2many(
        comodel_name='podiatry.prescription',
        inverse_name='patient_id',
        string="Prescriptions",
    )
    

    prescription_line = fields.One2many(
        'podiatry.prescription.line', 'name', 'Prescription Line')

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['podiatry.prescription'].search_count(
                [('patient_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Created by",
    )

    # partner_id = fields.Many2one(
    #     comodel_name='res.partner', string="Contact",
    # )
    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='cascade',
                                 help='Partner-related data of the Patient')

    def unlink(self):
        self.partner_id.unlink()
        return super(Patient, self).unlink()

    other_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='podiatry_patient_partners_rel',
        column1='patient_id', column2='partner_id',
        string="Other Contacts",
    )

    diagnosis_id = fields.Many2one(
        comodel_name='podiatry.patient.diagnosis',
        string='Diagnosis')

    photo = fields.Binary(string="Picture")

    shoe_type = fields.Selection([('dress', 'Dress'), ('casual', 'Casual'), (
        'athletic', 'Athletic'), ('other', 'Other')], string='Shoe Type')

    other_shoe_type = fields.Char('Other Shoe Type')

    attachment_ids = fields.Many2many('ir.attachment', 'patient_ir_attachments_rel',
                                      'manager_id', 'attachment_id', string="Attachments",
                                      help="Patient Image / File Attachments")

    image1 = fields.Binary("Right photo")
    image2 = fields.Binary("Left photo")

    left_obj_model = fields.Binary("Left Obj")
    left_obj_file_name = fields.Char(string="Left Obj File Name")
    right_obj_model = fields.Binary("Right Obj")
    right_obj_file_name = fields.Char(string="Right Obj File Name")
    age = fields.Char(compute='_compute_age')

    @api.onchange('patient_id')
    def _onchange_patient(self):
        '''
        The purpose of the method is to define a domain.
        '''
        address_id = self.patient_id
        self.patient_address_id = address_id

    patient_address_id = fields.Many2one(
        'res.partner', string="Patient Address", )

    @api.onchange('practice_id')
    def onchange_practice_id(self):
        for rec in self:
            return {'domain': {'practitioner_id': [('practice_id', '=', rec.practice_id.id)]}}

    @api.model
    def _relativedelta_to_text(self, delta):
        result = []

        if delta:
            if delta.years > 0:
                result.append(
                    "{years} {practice}".format(
                        years=delta.years,
                        practice=_("year") if delta.years == 1 else _("years"),
                    )
                )
            if delta.months > 0 and delta.years < 9:
                result.append(
                    "{months} {practice}".format(
                        months=delta.months,
                        practice=_("month") if delta.months == 1 else _(
                            "months"),
                    )
                )
            if delta.days > 0 and not delta.years:
                result.append(
                    "{days} {practice}".format(
                        days=delta.days,
                        practice=_("day") if delta.days == 1 else _("days"),
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
        comodel_name='podiatry.patient',
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

    same_reference_patient_id = fields.Many2one(
        comodel_name='podiatry.patient',
        string='Patient with same Identity',
        compute='_compute_same_reference_patient_id',
    )

    @api.depends('reference')
    def _compute_same_reference_patient_id(self):
        for patient in self:
            domain = [
                ('reference', '=', patient.reference),
            ]

            origin_id = patient._origin.id

            if origin_id:
                domain += [('id', '!=', origin_id)]

            patient.same_reference_patient_id = bool(patient.reference) and \
                self.with_context(active_test=False).sudo().search(
                    domain, limit=1)

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'podiatry', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _add_followers(self):
        for patient in self:
            partner_ids = (patient.user_id.partner_id |
                           patient.responsible_id.partner_id).ids
            patient.message_subscribe(partner_ids=partner_ids)

    # @api.model
    # def create(self, vals):
    #     if not vals.get('notes'):
    #         vals['notes'] = 'New Patient'
    #     if vals.get('reference', _('New')) == _('New'):
    #         vals['reference'] = self.env['ir.sequence'].next_by_code(
    #             'podiatry.patient') or _('New')
    #     patient = super(Patient, self).create(vals)
    #     patient._add_followers()
    #     return patient
    
    def _valid_field_parameter(self, field, name):
            return name == 'sort' or super()._valid_field_parameter(field, name)

    
    @api.model
    def create(self,vals):
        prescription = self._context.get('prescription_id')
        res_partner_obj = self.env['res.partner']
        if prescription:
            val_1 = {'name': self.env['res.partner'].browse(vals['patient_id']).name}
            patient= res_partner_obj.create(val_1)
            vals.update({'patient_id': patient.id})
        if vals.get('date_of_birth'):
            dt = vals.get('date_of_birth')
            d1 = datetime.strptime(str(dt), "%Y-%m-%d").date()
            d2 = datetime.today().date()
            rd = relativedelta(d2, d1)
            age = str(rd.years) + "y" +" "+ str(rd.months) + "m" +" "+ str(rd.days) + "d"
            vals.update({'age':age} )
        if not vals.get('notes'):
                vals['notes'] = 'New Patient'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'podiatry.patient') or _('New')
        patient = super(Patient, self).create(vals)
        return patient

        # patient_id  = self.env['ir.sequence'].next_by_code('podiatry.patient')
        # if patient_id:
        #     val.update({
        #                 'name':patient_id,
        #                })
        # result = super(Patient, self).create(val)
        # return result

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.reference + '] ' + rec.name
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(Patient, self).write(values)
        if 'user_id' in values or 'other_partner_ids' in values:
            self._add_followers()
        return result

    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'podiatry.prescription',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
