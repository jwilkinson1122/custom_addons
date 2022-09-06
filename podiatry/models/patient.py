# See LICENSE file for full copyright and licensing details.

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.modules import get_module_resource

from . import podiatry

# from lxml import etree
# added import statement in try-except because when server runs on
# windows operating system issue arise because this library is not in Windows.
try:
    from odoo.tools import image_colorize
except:
    image_colorize = False


class PatientPatient(models.Model):
    '''Defining a patient information.'''

    _name = 'patient.patient'
    _table = "patient_patient"
    _description = 'Patient Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        '''Method to get patient of parent having group doctor'''
        doctor_group = self.env.user.has_group(
            'podiatry.group_podiatry_doctor')
        parent_grp = self.env.user.has_group('podiatry.group_podiatry_parent')
        login_user_rec = self.env.user
        name = self._context.get('patient_id')
        if name and doctor_group and parent_grp:
            parent_login_pat_rec = self.env['podiatry.parent'].search([
                ('partner_id', '=', login_user_rec.partner_id.id)])
            childrens = parent_login_pat_rec.patient_id
            args.append(('id', 'in', childrens.ids))
        return super(PatientPatient, self)._search(
            args=args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)

    @api.depends('date_of_birth')
    def _compute_patient_age(self):
        '''Method to calculate patient age'''
        current_dt = fields.Date.today()
        for rec in self:
            rec.age = 0
            if rec.date_of_birth and rec.date_of_birth < current_dt:
                start = rec.date_of_birth
                age_calc = ((current_dt - start).days / 365)
                # Age should be greater than 0
                if age_calc > 0.0:
                    rec.age = age_calc

    @api.model
    def _default_image(self):
        '''Method to get default Image'''
        image_path = get_module_resource('hr', 'static/src/img',
                                         'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    @api.depends('state')
    def _compute_doctor_user(self):
        '''Compute doctor boolean field if user form doctor group'''
        doctor = self.env.user.has_group("podiatry.group_podiatry_doctor")
        for rec in self:
            rec.doctor_user_grp = False
            if doctor and rec.state == 'done':
                rec.doctor_user_grp = True

    @api.model
    def check_current_year(self):
        '''Method to get default value of logged in Patient'''
        res = self.env['academic.year'].search([('current', '=', True)])
        if not res:
            raise ValidationError(_(
                "There is no current Academic Year defined! Please contact Administator!"))
        return res.id

    family_con_ids = fields.One2many('patient.family.contact',
                                     'family_contact_id', 'Family Contact Detail',
                                     states={'done': [('readonly', True)]},
                                     help='Select the patient family contact')
    user_id = fields.Many2one('res.users', 'User ID', ondelete="cascade",
                              required=True, delegate=True,
                              help='Select related user of the patient')
    patient_name = fields.Char('Patient Name', related='user_id.name',
                               store=True, readonly=True, help='Patient Name')
    pid = fields.Char('Patient ID', required=True,
                      default=lambda self: _('New'), help='Personal IDentification Number')
    reg_code = fields.Char('Registration Code',
                           help='Patient Registration Code')
    patient_code = fields.Char('Patient Code', help='Enter patient code')
    contact_phone = fields.Char('Phone no.', help='Enter patient phone no.')
    contact_mobile = fields.Char('Mobile no', help='Enter patient mobile no.')
    roll_no = fields.Integer('Roll No.', readonly=True,
                             help='Enter patient roll no.')
    photo = fields.Binary('Photo', default=_default_image,
                          help='Attach patient photo')
    year = fields.Many2one('academic.year', 'Academic Year', readonly=True,
                           default=check_current_year, help='Select academic year',
                           tracking=True)
    cast_id = fields.Many2one('patient.cast', 'Religion/Caste',
                              help='Select patient cast')
    relation = fields.Many2one('patient.relation.master', 'Relation',
                               help='Select patient relation')

    register_date = fields.Date('Registration Date', default=fields.Date.today(),
                                help='Enter patient register date')
    middle = fields.Char('Middle Name', required=True,
                         states={'done': [('readonly', True)]},
                         help='Enter patient middle name')
    last = fields.Char('Surname', required=True,
                       states={'done': [('readonly', True)]}, help='Enter patient last name')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              'Gender', states={'done': [('readonly', True)]},
                              help='Select patient gender')
    date_of_birth = fields.Date('BirthDate', required=True,
                                states={'done': [('readonly', True)]},
                                help='Enter patient date of birth')
    mother_tongue = fields.Many2one('mother.toungue', "Mother Tongue",
                                    help='Select patient mother tongue')
    age = fields.Integer(compute='_compute_patient_age', string='Age',
                         readonly=True, help='Enter patient age')
    maritual_status = fields.Selection([('unmarried', 'Unmarried'),
                                        ('married', 'Married')], 'Marital Status',
                                       states={'done': [('readonly', True)]},
                                       help='Select patient maritual status')
    reference_ids = fields.One2many('patient.reference', 'reference_id',
                                    'References', states={'done': [('readonly', True)]},
                                    help='Enter patient references')
    previous_podiatry_ids = fields.One2many('patient.previous.podiatry',
                                            'previous_podiatry_id', 'Previous Practice Detail',
                                            states={
                                                'done': [('readonly', True)]},
                                            help='Enter patient podiatry details')
    doctor = fields.Char('Doctor Name', states={'done': [('readonly', True)]},
                         help='Enter doctor name for patient medical details')
    designation = fields.Char('Designation', help='Enter doctor designation')
    doctor_phone = fields.Char('Contact No.', help='Enter doctor phone')
    blood_group = fields.Char('Blood Group', help='Enter patient blood group')
    height = fields.Float('Height', help="Hieght in C.M")
    weight = fields.Float('Weight', help="Weight in K.G")
    eye = fields.Boolean('Eyes', help='Eye for medical info')
    ear = fields.Boolean('Ears', help='Eye for medical info')
    nose_throat = fields.Boolean('Nose & Throat',
                                 help='Nose & Throat for medical info')
    respiratory = fields.Boolean('Respiratory',
                                 help='Respiratory for medical info')
    cardiovascular = fields.Boolean('Cardiovascular',
                                    help='Cardiovascular for medical info')
    neurological = fields.Boolean('Neurological',
                                  help='Neurological for medical info')
    muskoskeletal = fields.Boolean('Musculoskeletal',
                                   help='Musculoskeletal for medical info')
    dermatological = fields.Boolean('Dermatological',
                                    help='Dermatological for medical info')
    blood_pressure = fields.Boolean('Blood Pressure',
                                    help='Blood pressure for medical info')
    remark = fields.Text('Remark', states={'done': [('readonly', True)]},
                         help='Remark can be entered if any')
    podiatry_id = fields.Many2one('podiatry.podiatry', 'Podiatry',
                                  states={'done': [('readonly', True)]}, help='Select podiatry', tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'),
                              ('terminate', 'Terminate'), ('cancel', 'Cancel'),
                              ('archive', 'Archive')], 'Status', readonly=True, default="draft",
                             tracking=True, help='State of the patient registration form')
    history_ids = fields.One2many('patient.history', 'patient_id', 'History',
                                  help='Enter patient history')
    certificate_ids = fields.One2many('patient.certificate', 'patient_id',
                                      'Certificate', help='Enter patient certificates')
    patient_discipline_line = fields.One2many('patient.descipline',
                                              'patient_id', 'Descipline',
                                              help='''Enter patient descipline info''')
    document = fields.One2many('patient.document', 'doc_id', 'Documents',
                               help='Attach patient documents')
    description = fields.One2many('patient.description', 'des_id',
                                  'Description', help='Description')
    award_list = fields.One2many('patient.award', 'award_list_id',
                                 'Award List', help='Patient award list')
    pt_name = fields.Char('First Name', related='user_id.name',
                          readonly=True, help='Enter patient first name', tracking=True)
    Acadamic_year = fields.Char('Year', related='year.name',
                                help='Academic Year', readonly=True, tracking=True)
    division_id = fields.Many2one('standard.division', 'Division',
                                  help='Select patient standard division', tracking=True)
    medium_id = fields.Many2one('standard.medium', 'Medium',
                                help='Select patient standard medium', tracking=True)
    standard_id = fields.Many2one('podiatry.standard', 'Class',
                                  help='Select patient standard', tracking=True)
    parent_id = fields.Many2many('podiatry.parent', 'patients_parents_rel',
                                 'patient_id', 'patients_parent_id', 'Parent(s)',
                                 states={'done': [('readonly', True)]},
                                 help='Enter patient parents')
    terminate_reason = fields.Text('Reason',
                                   help='Enter patient terminate reason', tracking=True)
    active = fields.Boolean(default=True,
                            help='Activate/Deactivate patient record', tracking=True)
    doctor_user_grp = fields.Boolean("Doctor Group",
                                     compute="_compute_doctor_user",
                                     help='Activate/Deactivate doctor group')

    @api.model
    def create(self, vals):
        '''Method to create user when patient is created'''
        if vals.get('pid', _('New')) == _('New'):
            vals['pid'] = self.env['ir.sequence'
                                   ].next_by_code('patient.patient'
                                                  ) or _('New')
        if vals.get('pid', False):
            vals['login'] = vals['pid']
            vals['password'] = vals['pid']
        else:
            raise UserError(_(
                "Error! PID not valid so record will not be saved."))
        if vals.get('company_id', False):
            company_vals = {'company_ids': [(4, vals.get('company_id'))]}
            vals.update(company_vals)
        if vals.get('email'):
            podiatry.emailvalidation(vals.get('email'))
        res = super(PatientPatient, self).create(vals)
        doctor = self.env['podiatry.doctor']
        for data in res.parent_id:
            for record in doctor.search([('pt_parent_id', '=', data.id)]):
                record.write({'patient_id': [(4, res.id, None)]})
        # Assign group to patient based on condition
        emp_grp = self.env.ref('base.group_user')
        if res.state == 'draft':
            register_group = self.env.ref('podiatry.group_is_register')
            new_grp_list = [register_group.id, emp_grp.id]
            res.user_id.write({'groups_id': [(6, 0, new_grp_list)]})
        elif res.state == 'done':
            done_patient = self.env.ref('podiatry.group_podiatry_patient')
            group_list = [done_patient.id, emp_grp.id]
            res.user_id.write({'groups_id': [(6, 0, group_list)]})
        return res

    def write(self, vals):
        '''Inherited method write to assign 
        patient to their respective doctor'''
        doctor = self.env['podiatry.doctor']
        if vals.get('parent_id'):
            for parent in vals.get('parent_id')[0][2]:
                for data in doctor.search([('pt_parent_id', '=', parent)]):
                    data.write({'patient_id': [(4, self.id)]})
        return super(PatientPatient, self).write(vals)

    @api.constrains('date_of_birth')
    def check_age(self):
        '''Method to check age should be greater than 6'''
        if self.date_of_birth:
            start = self.date_of_birth
            age_calc = ((fields.Date.today() - start).days / 365)
            # Check if age less than required age
            if age_calc < self.podiatry_id.required_age:
                raise ValidationError(_(
                    "Age of patient should be greater than %s years!" % (
                        self.podiatry_id.required_age)))

    def set_to_draft(self):
        '''Method to change state to draft'''
        self.state = 'draft'

    def set_archive(self):
        '''Method to change state to archive'''
        for rec in self:
            rec.state = 'archive'
            rec.standard_id._compute_total_patient()
            rec.active = False
            rec.user_id.active = False

    def set_done(self):
        '''Method to change state to done'''
        self.state = 'done'

    def register_draft(self):
        '''Set the state to draft'''
        self.state = 'draft'

    def set_terminate(self):
        '''Set the state to terminate'''
        self.state = 'terminate'

    def cancel_register(self):
        '''Set the state to cancel.'''
        self.state = 'cancel'

    def register_done(self):
        '''Method to confirm register'''
        podiatry_standard_obj = self.env['podiatry.standard']
        ir_sequence = self.env['ir.sequence']
        patient_group = self.env.ref('podiatry.group_podiatry_patient')
        emp_group = self.env.ref('base.group_user')
        for rec in self:
            if not rec.standard_id:
                raise ValidationError(_("Please select class!"))
            if rec.standard_id.remaining_seats <= 0:
                raise ValidationError(_('Seats of class %s are full'
                                        ) % rec.standard_id.standard_id.name)
            domain = [('podiatry_id', '=', rec.podiatry_id.id)]
            # Checks the standard if not defined raise error
            if not podiatry_standard_obj.search(domain):
                raise UserError(_(
                    "Warning! The standard is not defined in podiatry!"))
            # Assign group to patient
            rec.user_id.write({'groups_id': [(6, 0,
                                              [emp_group.id, patient_group.id])]})
            # Assign roll no to patient
            number = 1
            for rec_std in rec.search(domain):
                rec_std.roll_no = number
                number += 1
            # Assign registration code to patient
            reg_code = ir_sequence.next_by_code('patient.registration')
            registation_code = (str(rec.podiatry_id.state_id.name) + str('/') +
                                str(rec.podiatry_id.city) + str('/') +
                                str(rec.podiatry_id.name) + str('/') +
                                str(reg_code))
            pt_code = ir_sequence.next_by_code('patient.code')
            patient_code = (str(rec.podiatry_id.code) + str('/') +
                            str(rec.year.code) + str('/') +
                            str(pt_code))
            rec.write({'state': 'done',
                       'register_date': fields.Date.today(),
                       'patient_code': patient_code,
                       'reg_code': registation_code})
            template = self.env['mail.template'].sudo().search([
                ('name', 'ilike', 'Registration Confirmation')], limit=1)
            if template:
                for user in rec.parent_id:
                    subject = _("About Registration Confirmation")
                    if user.email:
                        body = """
                        <div>
                            <p>Dear """ + str(user.display_name) + """,
                            <br/><br/>
                            Registration of """+str(rec.display_name)+""" has been confirmed in """+str(rec.podiatry_id.name)+""".
                            <br></br>
                            Thank You.
                        </div>
                        """
                        template.send_mail(rec.id, email_values={
                            'email_from': self.env.user.email or '',
                            'email_to': user.email,
                            'subject': subject,
                            'body_html': body,
                        }, force_send=True)
        return True
