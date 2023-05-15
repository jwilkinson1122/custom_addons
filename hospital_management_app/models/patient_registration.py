# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class HospitalPatient(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string='Is Patient', tracking=True)

    # Personal Information
    registration_no = fields.Char(string='Registration_no')

    patient_registration = fields.Selection([('date_of_birth', 'DOB'), ('age_at_registration', 'Age at Registration')],
                                            string="Registration Type", tracking=True)
    date_of_birth = fields.Date(string="Date of Birth")
    months_registration = fields.Integer(string="Months")
    year_registration = fields.Integer(string="Years")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Others')], string="Gender",
                              tracking=True)
    marital_status = fields.Selection(
        [('um', 'UNMARRIED'), ('m', 'MARRIED'), ('w', 'WIDOWER'), ('d', 'DIVORCED'), ('x', 'SEPERATED'), ('w', 'WIDOW'),
         ('o', 'OTHERS'), ('un', 'UNKNOWN')], string='Marital Status', tracking=True)
    father_name = fields.Char(string="Father/Spouse's Name")
    education = fields.Selection(
        [('ILL', 'ILLITERATE'), ('LIT', 'LITERATE'), ('PRI', 'PRIMARY'), ('MID', 'MIDDLE'), ('SEC', 'SECONDARY'),
         ('TEC', 'TECHNICAL'), ('CAA', 'COLLEGE AND ABOVE'), ('OTH', 'OTHERS'), ('UNK', 'UNKNOWN'),
         ('LTY', 'LESS THAN 5 YRS OLD')], string='Education', tracking=True)
    occupation = fields.Selection(
        [('BUS', 'BUSINESS'), ('HW', 'HOUSE WIFE'), ('SER', 'SERVICE'), ('PEN', 'PENSIONER'), ('RET', 'RETIRED'),
         ('STD', 'STUDENT'), ('UNE', 'UNEMPLOYED'), ('OTH', 'OTHERS'), ('AGR', 'AGRICULTURE'), ('UNK', 'UNKNOWN')],
        string='Occupation', tracking=True)
    family_income = fields.Float(string="Family Income Monthly (Rs.)")
    nationality = fields.Selection(
        [('select', 'Select Nationality'), ('IND', 'INDIAN'), ('FOR', 'FOREIGN'), ('UN', 'UNKNOWN')],
        string="Nationality", )
    passport_no = fields.Char(string="Passport No.")
    passport_date = fields.Date(string="Passport Valid Till Date")
    religion = fields.Selection(
        [('select', 'Select Religion'), ('AIND', 'ANGLO INDIAN'), ('CHR', 'CHRISTIAN'), ('HIN', 'HINDU'),
         ('JAI', 'JAIN'), ('JEW', 'JEW'), ('MUS', 'MUSLIM'), ('NEB', 'NEO-BUDDHIST'), ('OTH', 'OTHERS'),
         ('PAR', 'PARSI'), ('SIK', 'SIKH'), ('UN', 'UNKNOWN')], string="Religion", tracking=True)
    mother_tongue = fields.Selection(
        [('select', 'Select Mother Tongue'), ('ASS', 'ASSAMESE'), ('BEN', 'BENGALI'), ('ENG', 'ENGLISH'),
         ('GUJ', 'GUJARATI'), ('HIN', 'HINDI'), ('KAN', 'KANNADA'), ('KAS', 'KASHMIRI'), ('KON', 'kONKANI'),
         ('MAL', 'MALAYALAM'), ('MARA', 'MARATHI'), ('MAR', 'MARWADI'), ('NEP', 'NEPALI'), ('ORI', 'ORIYA'),
         ('OTH', 'OTHERS'), ('PUN', 'PUNJABI'), ('RAJ', 'RAJASTHANI'), ('SAN', 'SANSKRIT'), ('SID', 'SINDHI'),
         ('TAM', 'TAMIL'), ('TEL', 'TELUGU'), ('TUL', 'TULU'), ('UN', 'UNKNOWN')], string="Mother Tongue",
        tracking=True)
    pan_no = fields.Char(string="Pan No.")
    registration_card = fields.Char(string="Registration Card")
    aadhaar_no = fields.Char(string="Aadhaar Number.")

    disease_type_id = fields.Many2one('disease.type', string='Disease Type', tracking=True)
    disease_stage_id = fields.Many2one('disease.stage', string='Disease Stage', tracking=True)
    disease_fees = fields.Float(string='Disease Fees Per Visit', related='disease_type_id.fees', store=True, tracking=True)
    no_of_appointment = fields.Integer('No Of Appointment', compute='compute_no_of_appointment')

    def compute_no_of_appointment(self):
        for rec in self:
            appointment_ids = self.env['appointment.management'].search(
                [('partner_id', '=', rec.id), ('doc_type', '=', 'appointment')])
            self.no_of_appointment = len(appointment_ids)

    def action_view_appointment(self):
        xml_id = 'hospital_management_app.appointment_management_view_tree_new'
        tree_view_id = self.env.ref(xml_id).id
        xml_id = 'hospital_management_app.appointment_management_view_form_new'
        form_view_id = self.env.ref(xml_id).id
        return {
            'name': _('Appointment'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'appointment.management',
            'context': {
                'default_partner_id': self.id,
                'default_disease_stage_id': self.disease_stage_id.id,
                'default_disease_type_id': self.disease_type_id.id,
                'default_father_name': self.father_name,
                'default_street': self.street,
                'default_street2': self.street2,
                'default_zip': self.zip,
                'default_city': self.city,
                'default_type': 'appointment',
                'default_registration_no': self.registration_no,
            },
            'domain': [('partner_id', '=', self.id), ('type', '=', 'appointment')],
            'type': 'ir.actions.act_window',
        }

    def action_add_reg_no(self):
        for rec in self:
            rec.registration_no = rec.env['ir.sequence'].next_by_code('res.partner.patient')

            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = \
                    ir_model_data._xmlid_to_res_id('hospital_management_app.email_template_send_registration_no')
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data._xmlid_to_res_id('mail.email_compose_message_wizard_form')
            except ValueError:
                compose_form_id = False
            ctx = {
                'default_model': 'res.partner',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'proforma': self.env.context.get('proforma', False),
                'force_email': True
            }
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }

    def send_birthday_wish(self):
        for rec in self:
            print('hiiiiii--------------------------')
            user_id = rec.create_uid
            template = self.env.ref('hospital_management_app.email_template_send_birthday')
            ctx = self._context.copy()
            template.with_context(ctx).send_mail(user_id.id, force_send=True)

            # self.ensure_one()
            # ir_model_data = self.env['ir.model.data']
            # try:
            #     template_id = \
            #         ir_model_data.get_object_reference('hospital_management_app',
            #                                            'email_template_send_birthday')[1]
            # except ValueError:
            #     template_id = False
            # try:
            #     compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            # except ValueError:
            #     compose_form_id = False
            # ctx = {
            #     'default_model': 'res.partner',
            #     'default_res_id': self.ids[0],
            #     'default_use_template': bool(template_id),
            #     'default_template_id': template_id,
            #     'default_composition_mode': 'comment',
            #     'mark_so_as_sent': True,
            #     'proforma': self.env.context.get('proforma', False),
            #     'force_email': True
            # }
            # return {
            #     'type': 'ir.actions.act_window',
            #     'view_type': 'form',
            #     'view_mode': 'form',
            #     'res_model': 'mail.compose.message',
            #     'views': [(compose_form_id, 'form')],
            #     'view_id': compose_form_id,
            #     'target': 'new',
            #     'context': ctx,
            # }

    # Permanent Address
    # street = fields.Char(string='Street')
    # street2 = fields.Char(string='Street2')
    # zip = fields.Char(string='Zip')
    # city = fields.Char(string='City')
    # state_id = fields.Many2one('res.country.state')
    # country_id = fields.Many2one('res.country')
