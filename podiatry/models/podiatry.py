# See LICENSE file for full copyright and licensing details.

# import time
import calendar
import re

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _

EM = (r"[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$")


def emailvalidation(email):
    """Check valid email."""
    if email:
        email_regex = re.compile(EM)
        if not email_regex.match(email):
            raise ValidationError(_("""This seems not to be valid email.
Please enter email in correct format!"""))


class AcademicYear(models.Model):
    '''Defines an academic year.'''

    _name = "academic.year"
    _description = "Academic Year"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True,
                              help="Sequence order you want to see this year.")
    name = fields.Char('Name', required=True, help='Name of academic year')
    code = fields.Char('Code', required=True, help='Code of academic year')
    date_start = fields.Date('Start Date', required=True,
                             help='Starting date of academic year')
    date_stop = fields.Date('End Date', required=True,
                            help='Ending of academic year')
    month_ids = fields.One2many('academic.month', 'year_id', 'Months',
                                help="Related Academic months")
    grade_id = fields.Many2one('grade.master', "Grade", help='Grade')
    current = fields.Boolean('Current', help="Set Active Current Year")
    description = fields.Text('Description', help='Description')

    @api.model
    def next_year(self, sequence):
        '''This method assign sequence to years'''
        year_rec = self.search([('sequence', '>', sequence)], order='id',
                               limit=1)
        if year_rec:
            return year_rec.id or False

    def name_get(self):
        '''Method to display name and code'''
        return [(rec.id, ' [' + rec.code + ']' + rec.name) for rec in self]

    def generate_academicmonth(self):
        """Generate academic months."""
        interval = 1
        month_obj = self.env['academic.month']
        for rec in self:
            start_date = rec.date_start
            while start_date < rec.date_stop:
                end_date = start_date + relativedelta(months=interval, days=-1)
                if end_date > rec.date_stop:
                    end_date = rec.date_stop
                month_obj.create({
                    'name': start_date.strftime('%B'),
                    'code': start_date.strftime('%m/%Y'),
                    'date_start': start_date,
                    'date_stop': end_date,
                    'year_id': rec.id,
                })
                start_date = start_date + relativedelta(months=interval)

    @api.constrains('date_start', 'date_stop')
    def _check_academic_year(self):
        '''Method to check start date should be greater than end date
           also check that dates are not overlapped with existing academic
           year'''
        new_start_date = self.date_start
        new_stop_date = self.date_stop
        delta = new_stop_date - new_start_date
        if delta.days > 365 and not calendar.isleap(new_start_date.year):
            raise ValidationError(_(
                "The duration of the academic year is invalid."))
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise ValidationError(_(
                "The start date of the academic year should be less than end date."))
        for old_ac in self.search([('id', 'not in', self.ids)]):
            # Check start date should be less than stop date
            if (old_ac.date_start <= self.date_start <= old_ac.date_stop or
                    old_ac.date_start <= self.date_stop <= old_ac.date_stop):
                raise ValidationError(_(
                    "Error! You cannot define overlapping academic years."))

    # @api.constrains('current')
    # def check_current_year(self):
    #     '''Constraint on active current year'''
    #     current_year_rec = self.search_count([('current', '=', True)])
    #     if current_year_rec >= 2:
    #         raise ValidationError(_(
    #             "Error! You cannot set two current year active!"))


class AcademicMonth(models.Model):
    '''Defining a month of an academic year.'''

    _name = "academic.month"
    _description = "Academic Month"
    _order = "date_start"

    name = fields.Char('Name', required=True, help='Name')
    code = fields.Char('Code', required=True, help='Code')
    date_start = fields.Date('Start of Period', required=True,
                             help='Start date')
    date_stop = fields.Date('End of Period', required=True,
                            help='End Date')
    year_id = fields.Many2one('academic.year', 'Academic Year', required=True,
                              help="Related academic year ")
    description = fields.Text('Description', help='Description')

    _sql_constraints = [
        ('month_unique', 'unique(date_start, date_stop, year_id)',
         'Academic Month should be unique!'),
    ]

    @api.constrains('year_id', 'date_start', 'date_stop')
    def _check_year_limit(self):
        '''Method to check year limit'''
        if self.year_id and self.date_start and self.date_stop:
            if (self.year_id.date_stop < self.date_stop or
                    self.year_id.date_stop < self.date_start or
                    self.year_id.date_start > self.date_start or
                    self.year_id.date_start > self.date_stop):
                raise ValidationError(_(
                    "Some of the months periods overlap or is not in the academic year!"))

    @api.constrains('date_start', 'date_stop')
    def check_months(self):
        '''Method to check duration of date'''
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise ValidationError(_(
                "End of Period date should be greater than Start of Periods Date!"))
        """Check start date should be less than stop date."""
        exist_month_rec = self.search([('id', 'not in', self.ids)])
        for old_month in exist_month_rec:
            if old_month.date_start <= \
                    self.date_start <= old_month.date_stop \
                    or old_month.date_start <= \
                    self.date_stop <= old_month.date_stop:
                raise ValidationError(_(
                    "Error! You cannot define overlapping months!"))


class StandardMedium(models.Model):
    ''' Defining a medium(ENGLISH, HINDI, GUJARATI) related to standard'''

    _name = "standard.medium"
    _description = "Standard Medium"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True,
                              help='Sequence of the record')
    name = fields.Char('Name', required=True,
                       help='Medium of the standard')
    code = fields.Char('Code', required=True,
                       help='Medium code')
    description = fields.Text('Description', help='Description')


class StandardDivision(models.Model):
    '''Defining a division(A, B, C) related to standard'''

    _name = "standard.division"
    _description = "Standard Division"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True,
                              help='Sequence of the record')
    name = fields.Char('Name', required=True,
                       help='Division of the standard')
    code = fields.Char('Code', required=True,
                       help='Standard code')
    description = fields.Text('Description', help='Description')


class StandardStandard(models.Model):
    '''Defining Standard Information.'''

    _name = 'standard.standard'
    _description = 'Standard Information'
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True,
                              help='Sequence of the record')
    name = fields.Char('Name', required=True,
                       help='Standard name')
    code = fields.Char('Code', required=True,
                       help='Code of standard')
    description = fields.Text('Description', help='Description')

    @api.model
    def next_standard(self, sequence):
        '''This method check sequence of standard'''
        stand_rec = self.search([('sequence', '>', sequence)], order='id',
                                limit=1)
        return stand_rec and stand_rec.id or False


class PodiatryStandard(models.Model):
    '''Defining a standard related to podiatry.'''

    _name = 'podiatry.standard'
    _description = 'Practice Standards'
    _rec_name = "standard_id"

    @api.depends('standard_id', 'account_id', 'division_id', 'medium_id',
                 'account_id')
    def _compute_patient(self):
        '''Compute patient of done state'''
        patient_obj = self.env['patient.patient']
        for rec in self:
            rec.patient_ids = patient_obj.\
                search([('standard_id', '=', rec.id),
                        ('account_id', '=', rec.account_id.id),
                        ('division_id', '=', rec.division_id.id),
                        ('medium_id', '=', rec.medium_id.id),
                        ('state', '=', 'done')])

    @api.depends('subject_ids')
    def _compute_subject(self):
        '''Method to compute subjects.'''
        for rec in self:
            rec.total_no_subjects = len(rec.subject_ids)

    @api.depends('patient_ids')
    def _compute_total_patient(self):
        '''Method to compute total patient.'''
        for rec in self:
            rec.total_patients = len(rec.patient_ids)

    @api.depends("capacity", "total_patients")
    def _compute_remain_seats(self):
        '''Method to compute remaining seats.'''
        for rec in self:
            rec.remaining_seats = rec.capacity - rec.total_patients

    account_id = fields.Many2one('podiatry.podiatry', 'Practice Account', required=True,
                                 help='Practice Account of the following standard')
    standard_id = fields.Many2one('standard.standard', 'Standard',
                                  required=True, help='Standard')
    division_id = fields.Many2one('standard.division', 'Division',
                                  required=True, help='Standard division')
    medium_id = fields.Many2one('standard.medium', 'Medium', required=True,
                                help='Medium of the standard')
    subject_ids = fields.Many2many('subject.subject', 'subject_standards_rel',
                                   'subject_id', 'standard_id', 'Subject',
                                   help='Subjects of the standard')
    user_id = fields.Many2one('podiatry.doctor', 'Doctor',
                              help='Doctor of the standard')
    patient_ids = fields.One2many('patient.patient', 'standard_id',
                                  'Patient assigned',
                                  compute='_compute_patient', store=True,
                                  help='Patients which are in this standard'
                                  )
    color = fields.Integer('Color Index', help='Index of color')
    cmp_id = fields.Many2one('res.company', 'Company Name',
                             related='account_id.company_id', store=True,
                             help='Company_id of the podiatry')
    syllabus_ids = fields.One2many('subject.syllabus', 'standard_id',
                                   'Syllabus',
                                   help='Syllabus of the following standard')
    total_no_subjects = fields.Integer('Total No of Subject',
                                       compute="_compute_subject",
                                       help='Total subjects in the standard')
    name = fields.Char('Name', help='Standard name')
    capacity = fields.Integer("Total Seats", help='Standard capacity')
    total_patients = fields.Integer("Total Patients",
                                    compute="_compute_total_patient",
                                    store=True,
                                    help='Total patients of the standard')
    remaining_seats = fields.Integer("Available Seats",
                                     compute="_compute_remain_seats",
                                     store=True,
                                     help='Remaining seats of the standard')
    practice_location_id = fields.Many2one('practice.location', 'Location',
                                           help='Practice location of the account')

    @api.onchange('standard_id', 'division_id')
    def onchange_combine(self):
        '''Onchange to assign name respective of it's standard and division'''
        self.name = str(self.standard_id.name
                        ) + '-' + str(self.division_id.name)

    @api.constrains('standard_id', 'division_id')
    def check_standard_unique(self):
        """Method to check unique standard."""
        if self.env['podiatry.standard'].search([
            ('standard_id', '=', self.standard_id.id),
            ('division_id', '=', self.division_id.id),
            ('account_id', '=', self.account_id.id),
                ('id', 'not in', self.ids)]):
            raise ValidationError(_("Division and class should be unique!"))

    def unlink(self):
        """Method to check unique standard."""
        for rec in self:
            if rec.patient_ids or rec.subject_ids or rec.syllabus_ids:
                raise ValidationError(_(
                    "You cannot delete as it has reference with patient, subject or syllabus!"))
        return super(PodiatryStandard, self).unlink()

    @api.constrains('capacity')
    def check_seats(self):
        """Method to check seats."""
        if self.capacity <= 0:
            raise ValidationError(_("Total seats should be greater than 0!"))

    def name_get(self):
        '''Method to display standard and division'''
        return [(rec.id, rec.standard_id.name + '[' + rec.division_id.name +
                 ']') for rec in self]


class PodiatryPodiatry(models.Model):
    ''' Defining Account Information'''

    _name = 'podiatry.podiatry'
    _description = 'Account Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "com_name"

    account_id = fields.Char(string='Account Reference', required=True, copy=False, readonly=True,
                             default=lambda self: _('New Account'))

    active = fields.Boolean(string='Active', default=True, required=True, copy=True,
                            help='Activate/Deactivate account record', tracking=True)

    is_parent = fields.Boolean(string='Active', default=True, required=True, copy=True,
                               help='Activate/Deactivate account record', tracking=True)

    phone = fields.Char(string='Phone', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            valid_email = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                                   record.email)

            if valid_email is None:
                raise ValidationError('Please provide a valid E-mail')

    @api.constrains('code')
    def _check_code(self):
        for record in self:
            if self.env["podiatry.podiatry"].search(
                    [('account_id', '=', record.code), ('id', '!=', record.id)]):
                raise ValidationError("Account Code must be Unique")

    @api.model
    def _lang_get(self):
        '''Method to get language'''
        languages = self.env['res.lang'].search([])
        return [(language.code, language.name) for language in languages]

    company_id = fields.Many2one('res.company', 'Company', ondelete="cascade",
                                 required=True, delegate=True,
                                 help='Company_id of the podiatry')
    com_name = fields.Char('Practice Name', related='company_id.name',
                           store=True, help='Account Name')
    code = fields.Char('Code', required=False, help='Account code')

    # account_id = fields.Many2one('podiatry.podiatry', 'Practice Account', required=True,
    #                               help='Practice Account of the following standard')
    practices = fields.One2many('practice.location', 'account_id',
                                'Practices', help='Account practices')
    standards = fields.One2many('podiatry.standard', 'account_id',
                                'Standards', help='Account standard')
    lang = fields.Selection(_lang_get, 'Language',
                            help='''If the selected language is loaded in the
                                system, all documents related to this partner
                                will be printed in this language.
                                If not, it will be English.''')

    @api.model
    def create(self, vals):
        if vals.get('account_id', _('New Account')) == _('New Account'):
            vals['account_id'] = self.env['ir.sequence'].next_by_code(
                'podiatry.podiatry') or _('New Account')

        res = super(PodiatryPodiatry, self).create(vals)
        main_company = self.env.ref('base.main_company')
        res.company_id.parent_id = main_company.id
        return res


class PatientDocument(models.Model):
    """Defining Patient document."""
    _name = 'patient.document'
    _description = "Patient Document"
    _rec_name = "doc_type"

    doc_id = fields.Many2one('patient.patient', 'Patient',
                             help='Patient of the following doc')
    file_no = fields.Char('File No', readonly="1",
                          default=lambda obj: obj.env['ir.sequence'
                                                      ].next_by_code('patient.document'),
                          help='File no of the document')
    submited_date = fields.Date('Submitted Date',
                                help='Document submitted date')
    doc_type = fields.Many2one('document.type', 'Document Type', required=True,
                               help='Document type')
    file_name = fields.Char('File Name', help='File name')
    return_date = fields.Date('Return Date', help='Document return date')
    new_datas = fields.Binary(
        'Attachments', help='Attachments of the document')


class DocumentType(models.Model):
    ''' Defining a Document Type(SSC,Leaving)'''
    _name = "document.type"
    _description = "Document Type"
    _rec_name = "doc_type"
    _order = "seq_no"

    seq_no = fields.Char('Sequence', readonly=True,
                         default=lambda self: _('New'), help='Sequence of the document')
    doc_type = fields.Char('Document Type', required=True,
                           help='Document type')

    @api.model
    def create(self, vals):
        if vals.get('seq_no', _('New')) == _('New'):
            vals['seq_no'] = self.env['ir.sequence'].next_by_code(
                'document.type') or _('New')
        return super(DocumentType, self).create(vals)


class PatientDescription(models.Model):
    ''' Defining a Patient Description'''
    _name = 'patient.description'
    _description = "Patient Description"

    des_id = fields.Many2one('patient.patient', 'Patient Ref.',
                             help='Patient record from patients')
    name = fields.Char('Name', help='Description name')
    description = fields.Char('Description', help='Patient description')


class PatientHistory(models.Model):
    """Defining Patient History."""

    _name = "patient.history"
    _description = "Patient History"

    patient_id = fields.Many2one('patient.patient', 'Patient',
                                 help='Related Patient')
    academice_year_id = fields.Many2one('academic.year', 'Academic Year',
                                        help='Academice Year')
    standard_id = fields.Many2one('podiatry.standard', 'Standard',
                                  help='Standard of the following patient')
    percentage = fields.Float("Percentage", readonly=True,
                              help='Percentage of the patient')
    result = fields.Char('Result', readonly=True,
                         help='Result of the patient')


class PatientReference(models.Model):
    ''' Defining a patient reference information '''

    _name = "patient.reference"
    _description = "Patient Reference"

    reference_id = fields.Many2one('patient.patient', 'Patient',
                                   help='Patient reference')
    name = fields.Char('First Name', required=True,
                       help='Patient name')
    middle = fields.Char('Middle Name', required=True,
                         help='Patient middle name')
    last = fields.Char('Surname', required=True,
                       help='Patient last name')
    designation = fields.Char('Designation', required=True,
                              help='Patient designation')
    phone = fields.Char('Phone', required=True,  help='Patient phone')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              'Gender',  help='Patient gender')


class PatientPreviousPodiatry(models.Model):
    ''' Defining a patient previous podiatry information '''
    _name = "patient.previous.podiatry"
    _description = "Patient Previous Practice"

    previous_account_id = fields.Many2one('patient.patient', 'Patient',
                                          help='Related patient')
    name = fields.Char('Name', required=True,
                       help='Patient previous podiatry name')
    registration_no = fields.Char('Registry No.', required=True,
                                  help='Patient registration number')
    register_date = fields.Date('Registry Date',
                                help='Patient register date')
    exit_date = fields.Date('Exit Date',
                            help='Patient previous podiatry exit date')
    course_id = fields.Many2one('standard.standard', 'Course', required=True,
                                help='Patient gender')

    @api.constrains('register_date', 'exit_date')
    def check_date(self):
        new_dt = fields.Date.today()
        if (self.register_date and self.register_date >= new_dt) or (
                self.exit_date and self.exit_date >= new_dt):
            raise ValidationError(_(
                "Your register date and exit date should be less than current date!"))
        if (self.register_date and self.exit_date) and (
                self.register_date > self.exit_date):
            raise ValidationError(_(
                "Registry date should be less than exit date in previous podiatry!"))


class PatientRelationMaster(models.Model):
    ''' Patient Relation Information '''
    _name = "patient.relation.master"
    _description = "Patient Relation Master"

    name = fields.Char('Name', required=True, help="Enter Relation name")
    seq_no = fields.Integer('Sequence', help='Relation sequence')


class GradeMaster(models.Model):
    """Defining grade master."""

    _name = 'grade.master'
    _description = "Grade Master"

    name = fields.Char('Grade', required=True, help='Grade name')
    grade_ids = fields.One2many('grade.line', 'grade_id', 'Grade Lines',
                                help='Grade which are consider in this.')


class GradeLine(models.Model):
    """Defining grade line."""

    _name = 'grade.line'
    _description = "Grades"
    _rec_name = 'grade'

    from_mark = fields.Integer('From Marks', required=True,
                               help='The grade will starts from this marks.')
    to_mark = fields.Integer('To Marks', required=True,
                             help='The grade will ends to this marks.')
    grade = fields.Char('Grade', required=True, help="Grade")
    sequence = fields.Integer('Sequence', help="Sequence order of the grade.")
    fail = fields.Boolean('Fail', help='''If fail field is set to True,
it will allow you to set the grade as fail.''')
    grade_id = fields.Many2one("grade.master", 'Grade Ref.',
                               help='Related grade')
    name = fields.Char('Name', help='Grade name')

    @api.constrains('from_mark', 'to_mark')
    def check_marks(self):
        '''Method to check overlapping of Marks'''
        for rec in self:
            if (rec.to_mark < rec.from_mark):
                raise ValidationError(_(
                    "To Marks should be greater than From Marks!"))
            for line in self.search([('grade_id', '=', rec.grade_id.id),
                                    ('id', '!=', rec.id)]):
                if (line.from_mark <= rec.from_mark <= line.to_mark or
                        line.from_mark <= rec.to_mark <= line.to_mark):
                    raise ValidationError(_(
                        "Error! You cannot define overlapping Marks!"))


class PracticeLocation(models.Model):
    """Defining practice location (child/sub accounts)."""

    _name = "practice.location"
    _description = "Practice Location"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "com_name"

    name = fields.Char("Name", help='Practice name')
    account_id = fields.Many2one('podiatry.podiatry', 'Account', required=True,
                                 help='Parent Account')

    practice_id = fields.Char(string='Practice Reference', required=True, copy=False, readonly=True,
                              default=lambda self: _('New Practice'))

    active = fields.Boolean(string='Active', default=True, required=True, copy=True,
                            help='Activate/Deactivate practice record', tracking=True)

    phone = fields.Char(string='Phone', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            valid_email = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                                   record.email)

            if valid_email is None:
                raise ValidationError('Please provide a valid E-mail')

    @api.constrains('code')
    def _check_code(self):
        for record in self:
            if self.env["podiatry.podiatry"].search(
                    [('practice_id', '=', record.code), ('id', '!=', record.id)]):
                raise ValidationError("Practice Code must be Unique")

    # company_id = fields.Many2one('res.company', 'Company', ondelete="cascade",
    #                              required=True, delegate=True,
    #                              help='Company_id of the podiatry')
    # com_name = fields.Char('Practice Name', related='company_id.name',
    #                        store=True, help='Account Name')

    @api.model
    def create(self, vals):
        if vals.get('practice_id', _('New Practice')) == _('New Practice'):
            vals['account_id'] = self.env['ir.sequence'].next_by_code(
                'podiatry.podiatry') or _('New Account')

        res = super(PracticeLocation, self).create(vals)
        main_company = self.env.ref('base.main_company')
        res.company_id.parent_id = main_company.id
        return res


class Report(models.Model):
    _inherit = "ir.actions.report"

    def render_template(self, template, values=None):
        patient_id = self._context.get('patient_id')
        if patient_id:
            patient_rec = self.env['patient.patient'].browse(patient_id)
        if patient_rec and patient_rec.state == 'draft':
            raise ValidationError(_(
                "You cannot print report forpatient in unconfirm state!"))
        return super(Report, self).render_template(template, values)
