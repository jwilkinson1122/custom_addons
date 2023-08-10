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
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'patient_id'
 
 
    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='cascade', help='Partner-related data of the Patient')
    user_id = fields.Many2one(comodel_name='res.users', string="Created By", default=lambda self: self.env.user)
    # patient_id = fields.Many2one('res.partner', string="Patient", domain=[('is_patient','=',True)])
    patient_id = fields.Many2one('res.partner',domain=[('is_patient','=',True)],string='Patient')

    practice_id = fields.Many2one(comodel_name='podiatry.practice', required=True, string="Practice")
    practice_ids = fields.Many2many('podiatry.practice', 'patient_practice_rel', string='Practices')
    practitioner_id = fields.Many2one(comodel_name='podiatry.practitioner', required=True, string='Practitioner')
    practitioner_ids = fields.Many2many('podiatry.practitioner', 'patient_practitioner_rel', string='Practitioners')

    active = fields.Boolean(string="Active", default=True, tracking=True)
    color = fields.Integer(string="Color Index (0-15)")
    code = fields.Char(string="Code", copy=False)
    reference = fields.Char(string='Patient Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    birthdate = fields.Date(string="Date of Birth")
    notes = fields.Text(string="Notes")

    gender = fields.Selection(selection=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string="Gender")

    diagnosis = fields.Selection(selection=[
        ('plantar_fasciitis', 'Plantar Fasciitis'),
        ('diabetes', 'Diabetes'),
        ('other', 'Other'),
    ], string="Diagnosis")
    
    # weight = fields.Float("Weight")
    # weight_uom = fields.Many2one(
    #     "product.uom", "Weight UoM",
    #     domain=lambda self: [('category_id', '=',
    #                           self.env.ref('product.uom_categ_weight').id)]
    # )
    
    # height = fields.Float("Height")
    # height_uom = fields.Many2one(
    #     "product.uom", "Height UoM",
    #     domain=lambda self: [('category_id', '=',
    #                           self.env.ref('product.uom_categ_length').id)]
    # )


    signature = fields.Binary(string="Signature")

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')

    patient_prescription_ids = fields.One2many(
        "podiatry.prescription",
        "patient_id",
        string="Patients Prescriptions",
        domain=[("active", "=", True)],
    )

    prescription_device_lines = fields.One2many(
        'prescription.device.line', 'prescription_id', 'Prescription Line')

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['podiatry.prescription'].search_count(
                [('patient_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    diagnosis_id = fields.Many2one(comodel_name='podiatry.patient.diagnosis', string='Diagnosis')
    photo = fields.Binary(string="Picture")
    shoe_type = fields.Selection([('dress', 'Dress'), ('casual', 'Casual'), ('athletic', 'Athletic'), ('other', 'Other')], string='Shoe Type')

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

    patient_address_id = fields.Many2one('res.partner', string="Patient Address")

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

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'podiatry', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())
    
    def _valid_field_parameter(self, field, name):
            return name == 'sort' or super()._valid_field_parameter(field, name)

    def _add_followers(self):
        for patient in self:
            partner_ids = (patient.user_id.partner_id |
                           patient.responsible_id.partner_id).ids
            patient.message_subscribe(partner_ids=partner_ids)

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

    def name_get(self):
        result = []
        for rec in self:
            name =  rec.name
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(Patient, self).write(values)
        if 'user_id' in values:
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
    
    def unlink(self):
        self.partner_id.unlink()
        return super(Patient, self).unlink()
