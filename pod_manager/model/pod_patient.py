# -*- coding: utf-8 -*-


import string
from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


# from odoo import api, fields, models


# class device(models.Model):
#     _name = "device"
#     _description = "device"
#     _inherit = ["mail.thread", "mail.activity.mixin"]
#     _order = "name"

#     name = fields.Char(string="Name")
#     ref = fields.Char(string="Reference")
#     categories_id = fields.Many2one(
#         "device.categories", string="categories", required=True)
#     type_id = fields.Many2one("device.type", string="Type", required=True)
#     color_id = fields.Many2one("device.color", string="Color")
#     size = fields.Char(string="Size")
#     weight = fields.Float(string="Weight (in kg)")
#     birth_date = fields.Date(string="Birth Date")
#     gender = fields.Selection(
#         string="Gender",
#         selection=[
#             ("female", "Female"),
#             ("male", "Male"),
#             ("hermaphrodite", "Hermaphrodite"),
#             ("neutered", "Neutered"),
#         ],
#         default="female",
#         required=True,
#     )
#     active = fields.Boolean(default=True)
#     image = fields.Binary(
#         "Image", attachment=True, help="This field holds the photo of the device."
#     )

#     @api.onchange("categories_id")
#     def onchange_categories(self):
#         self.type_id = False

#     @api.onchange("type_id")
#     def onchange_type(self):
#         self.color_id = False


class pod_patient(models.Model):
    _name = 'pod.patient'
    # _inherit = ['res.partner', 'mail.thread', 'mail.activity.mixin']
    _description = 'podiatry patient'
    _rec_name = 'patient_id'

    @api.model
    def default_get(self, fields):
        result = super(pod_patient, self).default_get(fields)
        result['notes'] = 'Patient Notes'
        return result

    @api.onchange('patient_id')
    def _onchange_patient(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.patient_id
        self.partner_address_id = address_id

    def print_report(self):
        return self.env.ref('pod_manager.report_print_patient_card').report_action(self)

    def create_rx(self):
        return self.env.ref('pod_manager.action_view_prescription_id2')

    @api.depends('date_of_birth')
    def onchange_age(self):
        for rec in self:
            if rec.date_of_birth:
                d1 = rec.date_of_birth
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                rec.age = str(rd.years) + "y" + " " + \
                    str(rd.months) + "m" + " " + str(rd.days) + "d"
            else:
                rec.age = "Enter Date of Birth"

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')

    prescription_ids = fields.One2many(
        'pod.rx.order', 'patient_id', string="Prescriptions")

    patient_id = fields.Many2one('res.partner', domain=[(
        'is_patient', '=', True)], string="Patient", required=True)

    name = fields.Char(string='Patient', readonly=True)
    first_name = fields.Char('First Name')
    firstname = fields.Char('First Name')
    last_name = fields.Char('Last Name')
    lastname = fields.Char('Last Name')
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female')], string="Gender")
    weight = fields.Float("Weight")
    height = fields.Float("Height")
    shoe_size = fields.Float('Shoe Size')
    shoe_width = fields.Char('Shoe Width')

    shoe_type = fields.Selection(
        [('dress', 'Dress'), ('casual', 'Casual'), ('athletic', 'Athletic'), ('other', 'Other')], string='Shoe Type')

    other_shoe_type = fields.Char('Other Shoe Type')

    age = fields.Char(compute=onchange_age, string="Patient Age", store=True)

    patient_street = fields.Char('Street')
    patient_street2 = fields.Char('Street2')
    patient_city = fields.Char('City')
    patient_country_id = fields.Char('Country')
    patient_state_id = fields.Char('State')
    patient_zip = fields.Char('Zip')

    notes = fields.Text(string='Notes')

    practice_partner_id = fields.Many2one(
        'res.partner', domain=[('is_practice', '=', True)], string="Medical Center")

    partner_address_id = fields.Many2one(
        'res.partner', domain=[('is_practice', '=', True)], string="Practice", )

    # primary_care_doctor_id = fields.Many2one(
    #     'pod.doctor', string="Primary Doctor")

    primary_care_doctor_id = fields.Many2one(
        'res.partner', domain=[('is_doctor', '=', True)], string="Primary Doctor", )

    patient_condition_ids = fields.One2many(
        'pod.patient.condition', 'patient_id')

    report_date = fields.Date('Date', default=datetime.today().date())

    right_photo = fields.Image("Right Photo")
    left_photo = fields.Image("Left Photo")

    # documents = fields.Binary(string="Documents")
    # document_name = fields.Char(string="File Name")
    left_obj_model = fields.Binary("Left Obj")
    left_obj_file_name = fields.Char(string="Left Obj File Name")
    right_obj_model = fields.Binary("Right Obj")
    right_obj_file_name = fields.Char(string="Right Obj File Name")
    # left_obj_model = fields.Binary("Left Model")

    device_ids = fields.One2many(
        'pod.patient.device1', 'pod_patient_device_id')

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['pod.rx.order'].search_count(
                [('patient_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def create(self, val):

        res_partner_obj = self.env['res.partner']
        if not val.get('notes'):
            val['notes'] = 'New Patient'
        if val.get('date_of_birth'):
            dt = val.get('date_of_birth')
            d1 = datetime.strptime(str(dt), "%Y-%m-%d").date()
            d2 = datetime.today().date()
            rd = relativedelta(d2, d1)
            age = str(rd.years) + "y" + " " + str(rd.months) + \
                "m" + " " + str(rd.days) + "d"
            val.update({'age': age})

        patient_id = self.env['ir.sequence'].next_by_code('pod.patient')
        if patient_id:
            val.update({
                'name': patient_id,
            })
        result = super(pod_patient, self).create(val)
        return result

    # @api.constrains('name')
    # def check_name(self):
    #     for rec in self:
    #         patients = self.env['pod.patient'].search(
    #             [('name', '=', rec.name), ('id', '!=', rec.id)])
    #         if patients:
    #             raise ValidationError(_("Name %s Already Exists" % rec.name))

    # @api.constrains('age')
    # def check_age(self):
    #     for rec in self:
    #         if rec.age == 0:
    #             raise ValidationError(_("Age Cannot Be Zero .. !"))

    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         name = '[' + rec.reference + '] ' + rec.name
    #         result.append((rec.id, name))
    #     return result

    # def action_open_prescriptions(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Prescriptions',
    #         'res_model': 'pod.rx.order',
    #         'domain': [('patient_id', '=', self.id)],
    #         'context': {'default_patient_id': self.id},
    #         'view_mode': 'tree,form',
    #         'target': 'current',
    #     }

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
