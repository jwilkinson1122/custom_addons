# See LICENSE file for full copyright and licensing details.
import pytz
from datetime import datetime, time
from dateutil.rrule import rrule, DAILY
from random import choice
from string import digits
from werkzeug.urls import url_encode
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.osv.query import Query
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.osv import expression
from odoo.tools.misc import format_date


class PodiatryTeacher(models.Model):
    '''Defining a Teacher information.'''

    _name = 'podiatry.teacher'
    _description = 'Teacher Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one('res.partner', 'Partner ID',
        ondelete="cascade", delegate=True, required=True,
        help='Enter related partner')
    # company_id = fields.Many2one('res.company', 'Company', index=True)
    location_id = fields.Many2one('res.partner', 'Location', compute="_compute_location_id", store=True, readonly=False)
    address_id = fields.Many2one('res.partner', 'Location Address', compute="_compute_address_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    role_id = fields.Many2one(tracking=True)
    job_title = fields.Char("Job Title", compute="_compute_job_title", store=True, readonly=False)
    identification_id = fields.Char(string='Identification No', groups="base.group_user", tracking=True)
    standard_id = fields.Many2one('podiatry.standard',
        "Responsibility of Academic Class",
        help="Standard for which the teacher responsible for.")
    stand_id = fields.Many2one('standard.standard', "Course",
        related="standard_id.standard_id", store=True,
        help='''Select standard which are assigned to teacher''')
    subject_id = fields.Many2many('subject.subject', 'subject_teacher_rel',
        'teacher_id', 'subject_id', 'Course-Subjects',
        help='Select subject of teacher')
    clinic_id = fields.Many2one('podiatry.podiatry', "Clinic",
        help='Select Clinic')
    category_ids = fields.Many2many('res.partner.category',
        'teacher_category_rel', 'emp_id', 'categ_id', 'Tags',
        help='Select partner category')
    # department_id = fields.Many2one('res.partner', 'Department',
    #     help='Select department')
    department_id = fields.Many2one('res.partner', 'Department', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    manager_id = fields.Many2one('res.partner', string='Manager', tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    assistant_id = fields.Many2one(
        'res.partner', 'Assistant', compute='_compute_assistant', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Select the "Partner" who is the assistant.\n'
             'The "Assistant" has no specific rights or responsibilities by default.')
    is_parent = fields.Boolean('Is Parent',
        help='Select this if it parent')
    stu_parent_id = fields.Many2one('podiatry.parent', 'Related Parent',
        help='Enter student parent')
    student_id = fields.Many2many('student.student',
        'students_teachers_parent_rel', 'teacher_id', 'student_id',
        'Children', help='Select student')
    phone_numbers = fields.Char("Phone Number", help='Student PH no')
    notes = fields.Text('Note')
    personal_address_id = fields.Many2one(
        'res.partner', 'Address', help='Enter here the private address of the employee, not the one linked to company.',
        groups="base.group_user", tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    is_personal_address_a_company = fields.Boolean(
        'The partner address has a company linked',
        compute='_compute_is_personal_address_a_company',
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="base.group_user", tracking=True)
    birthday = fields.Date('Date of Birth', groups="base.group_user", tracking=True)


    @api.onchange('standard_id')
    def _onchange_standard_id(self):
        for rec in self:
            rec.clinic_id = (rec.standard_id and rec.standard_id.clinic_id and
                            rec.standard_id.clinic_id.id or False)

    @api.onchange('is_parent')
    def _onchange_isparent(self):
        """Onchange method for is parent"""
        self.stu_parent_id = False
        self.student_id = False

    @api.model
    def create(self, vals):
        """Inherited create method to assign value to users for delegation"""
        teacher_id = super(PodiatryTeacher, self).create(vals)
        user_obj = self.env['res.users']
        user_vals = {'name': teacher_id.name,
                     'login': teacher_id.email,
                     'email': teacher_id.email,
                     }
        ctx_vals = {'teacher_create': True,
                    'clinic_id': teacher_id.clinic_id.partner_id.id}
        user_rec = user_obj.with_context(ctx_vals).create(user_vals)
        teacher_id.partner_id.write({'user_id': user_rec.id})
#        if vals.get('is_parent'):
#            self.parent_crt(teacher_id)
        return teacher_id

# Removing this code because of issue faced due to email id of the
# user is same for parent and Teacher, and system will not allow it.
# now user shuld create Parent record first and then select it in
# related parent in Teacher Profile. - Anu Patel (24/03/2021)
#    def parent_crt(self, assistant_id):
#        """Method to create parent record based on parent field"""
#        stu_parent = []
#        if assistant_id.stu_parent_id:
#            stu_parent = assistant_id.stu_parent_id
#        if not stu_parent:
#            emp_user = assistant_id.partner_id
#            students = [stu.id for stu in assistant_id.student_id]
#            parent_vals = {'name': assistant_id.name,
#                           'email': emp_user.email,
#                           'user_ids': [(6, 0, [emp_user.user_id.id])],
#                           'partner_id': emp_user.user_id.partner_id.id,
#                           'student_id': [(6, 0, students)]}
#            stu_parent = self.env['podiatry.parent'].with_context().create(parent_vals)
#            assistant_id.write({'stu_parent_id': stu_parent.id})
#        user = stu_parent.user_ids
#        user_rec = user[0]
#        parent_grp_id = self.env.ref('podiatry.group_podiatry_parent')
#        groups = parent_grp_id
#        if user_rec.groups_id:
#            groups = user_rec.groups_id
#            groups += parent_grp_id
#        group_ids = [group.id for group in groups]
#        user_rec.write({'groups_id': [(6, 0, group_ids)]})

    @api.depends('company_id')
    def _compute_address_id(self):
        for partner in self:
            address = partner.company_id.partner_id.address_get(['default'])
            partner.address_id = address['default'] if address else False

    @api.depends('department_id')
    def _compute_parent_id(self):
        for partner in self.filtered('department_id.manager_id'):
            partner.parent_id = partner.department_id.manager_id

    @api.depends('address_id')
    def _compute_location_id(self):
        to_reset = self.filtered(lambda e: e.address_id != e.location_id.address_id)
        to_reset.location_id = False
        
    @api.depends('personal_address_id.parent_id')
    def _compute_is_personal_address_a_company(self):
        """Checks that chosen address (res.partner) is not linked to a company.
        """
        for partner in self:
            try:
                partner.is_personal_address_a_company = partner.personal_address_id.parent_id.id is not False
            except AccessError:
                partner.is_personal_address_a_company = False

    @api.depends('parent_id')
    def _compute_assistant(self):
        for partner in self:
            assistant = partner.parent_id
            previous_manager = partner._origin.parent_id
            if assistant and (partner.assistant_id == previous_manager or not partner.assistant_id):
                partner.assistant_id = assistant
            elif not partner.assistant_id:
                partner.assistant_id = False

    @api.depends('role_id')
    def _compute_job_title(self):
        for partner in self.filtered('role_id'):
            partner.job_title = partner.role_id.name

    def write(self, vals):
        """Inherited write method to assign groups based on parent field"""
        # if vals.get('is_parent'):
        #     self.parent_crt(self)
        if vals.get('student_id'):
            self.stu_parent_id.write({'student_id': vals.get('student_id')})
        if not vals.get('is_parent'):
            user_rec = self.partner_id.user_id
            parent_grp_id = self.env.ref('podiatry.group_podiatry_parent')
            groups = parent_grp_id
            if parent_grp_id in user_rec.groups_id:
                user_rec.write({'groups_id': [(3, parent_grp_id.id)]})
        return super(PodiatryTeacher, self).write(vals)

    @api.onchange('address_id')
    def onchange_address_id(self):
        """Onchange method for address."""
        if self.address_id:
            self.phone = self.address_id.phone or False,
            self.mobile = self.address_id.mobile or False

    @api.onchange('department_id')
    def onchange_department_id(self):
        """Onchange method for deepartment."""
        self.parent_id = (self.department_id and
                          self.department_id.assistant_id and
                          self.department_id.assistant_id.id) or False

    @api.onchange('user_id')
    def onchange_user(self):
        """Onchange method for user."""
        if self.user_id:
            self.name = self.name or self.user_id.name
            self.email = self.user_id.email
            self.image = self.image or self.user_id.image

    @api.onchange('clinic_id')
    def onchange_podiatry(self):
        """Onchange method for podiatry."""
        partner = self.clinic_id.partner_id.partner_id
        self.address_id = partner.id or False
        self.mobile = partner.mobile or False
        self.location_id = partner.id or False
        self.email = partner.email or False
        phone = partner.phone or False
        self.phone = phone or False
        self.phone_numbers = phone or False
