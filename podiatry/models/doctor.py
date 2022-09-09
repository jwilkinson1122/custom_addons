# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PodiatryDoctor(models.Model):
    '''Defining a Doctor information.'''

    _name = 'podiatry.doctor'
    _description = 'Doctor Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', 'Employee ID',
                                  ondelete="cascade", delegate=True, required=True,
                                  help='Enter related employee')
    standard_id = fields.Many2one('podiatry.standard',
                                  "Responsibility",
                                  help="Standard for which the doctor responsible for.")
    stand_id = fields.Many2one('standard.standard', "Course",
                               related="standard_id.standard_id", store=True,
                               help='''Select standard which are assigned to doctor''')
    subject_id = fields.Many2many('subject.subject', 'subject_doctor_rel',
                                  'doctor_id', 'subject_id', 'Course-Subjects',
                                  help='Select subject of doctor')
    account_id = fields.Many2one('podiatry.podiatry', "Location",
                                 help='Select Practice')
    category_ids = fields.Many2many('hr.employee.category',
                                    'doctor_category_rel', 'emp_id', 'categ_id', 'Tags',
                                    help='Select employee category')
    department_id = fields.Many2one('hr.department', 'Department',
                                    help='Select department')
    is_parent = fields.Boolean('Is Parent',
                               help='Select this if it parent')
    pt_parent_id = fields.Many2one('podiatry.parent', 'Related Parent',
                                   help='Enter patient parent')
    patient_id = fields.Many2many('patient.patient',
                                  'patients_doctors_parent_rel', 'doctor_id', 'patient_id',
                                  'Children', help='Select patient')
    phone_numbers = fields.Char("Phone Number", help='Patient PH no')

    @api.onchange('standard_id')
    def _onchange_standard_id(self):
        for rec in self:
            rec.account_id = (rec.standard_id and rec.standard_id.account_id and
                              rec.standard_id.account_id.id or False)

    @api.onchange('is_parent')
    def _onchange_isparent(self):
        """Onchange method for is parent"""
        self.pt_parent_id = False
        self.patient_id = False

    @api.model
    def create(self, vals):
        """Inherited create method to assign value to users for delegation"""
        doctor_id = super(PodiatryDoctor, self).create(vals)
        user_obj = self.env['res.users']
        user_vals = {'name': doctor_id.name,
                     'login': doctor_id.work_email,
                     'email': doctor_id.work_email,
                     }
        ctx_vals = {'doctor_create': True,
                    'account_id': doctor_id.account_id.company_id.id}
        user_rec = user_obj.with_context(ctx_vals).create(user_vals)
        doctor_id.employee_id.write({'user_id': user_rec.id})
#        if vals.get('is_parent'):
#            self.parent_crt(doctor_id)
        return doctor_id

# Removing this code because of issue faced due to email id of the
# user is same for parent and Doctor, and system will not allow it.
# now user shuld create Parent record first and then select it in
# related parent in Contact Profiles. - Anu Patel (24/03/2021)
#    def parent_crt(self, manager_id):
#        """Method to create parent record based on parent field"""
#        pt_parent = []
#        if manager_id.pt_parent_id:
#            pt_parent = manager_id.pt_parent_id
#        if not pt_parent:
#            emp_user = manager_id.employee_id
#            patients = [pt.id for stu in manager_id.patient_id]
#            parent_vals = {'name': manager_id.name,
#                           'email': emp_user.work_email,
#                           'user_ids': [(6, 0, [emp_user.user_id.id])],
#                           'partner_id': emp_user.user_id.partner_id.id,
#                           'patient_id': [(6, 0, patients)]}
#            pt_parent = self.env['podiatry.parent'].with_context().create(parent_vals)
#            manager_id.write({'pt_parent_id': pt_parent.id})
#        user = pt_parent.user_ids
#        user_rec = user[0]
#        parent_grp_id = self.env.ref('podiatry.group_podiatry_parent')
#        groups = parent_grp_id
#        if user_rec.groups_id:
#            groups = user_rec.groups_id
#            groups += parent_grp_id
#        group_ids = [group.id for group in groups]
#        user_rec.write({'groups_id': [(6, 0, group_ids)]})

    def write(self, vals):
        """Inherited write method to assign groups based on parent field"""
        # if vals.get('is_parent'):
        #     self.parent_crt(self)
        if vals.get('patient_id'):
            self.pt_parent_id.write({'patient_id': vals.get('patient_id')})
        if not vals.get('is_parent'):
            user_rec = self.employee_id.user_id
            parent_grp_id = self.env.ref('podiatry.group_podiatry_parent')
            groups = parent_grp_id
            if parent_grp_id in user_rec.groups_id:
                user_rec.write({'groups_id': [(3, parent_grp_id.id)]})
        return super(PodiatryDoctor, self).write(vals)

    @api.onchange('address_id')
    def onchange_address_id(self):
        """Onchange method for address."""
        if self.address_id:
            self.work_phone = self.address_id.phone or False,
            self.mobile_phone = self.address_id.mobile or False

    @api.onchange('department_id')
    def onchange_department_id(self):
        """Onchange method for deepartment."""
        self.parent_id = (self.department_id and
                          self.department_id.manager_id and
                          self.department_id.manager_id.id) or False

    @api.onchange('user_id')
    def onchange_user(self):
        """Onchange method for user."""
        if self.user_id:
            self.name = self.name or self.user_id.name
            self.work_email = self.user_id.email
            self.image = self.image or self.user_id.image

    @api.onchange('account_id')
    def onchange_podiatry(self):
        """Onchange method for podiatry."""
        partner = self.account_id.company_id.partner_id
        self.address_id = partner.id or False
        self.mobile_phone = partner.mobile or False
        self.work_location_id = partner.id or False
        self.work_email = partner.email or False
        phone = partner.phone or False
        self.work_phone = phone or False
        self.phone_numbers = phone or False
