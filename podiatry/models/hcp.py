# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PodiatryHCP(models.Model):
    '''Defining a HCP information.'''

    _name = 'podiatry.hcp'
    _description = 'HCP Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', 'Employee ID',
                                  ondelete="cascade", delegate=True, required=True,
                                  help='Enter related employee')
    standard_id = fields.Many2one('podiatry.standard',
                                  "Responsibility of Academic Class",
                                  help="Standard for which the hcp responsible for.")
    stand_id = fields.Many2one('standard.standard', "Course",
                               related="standard_id.standard_id", store=True,
                               help='''Select standard which are assigned to hcp''')
    subject_id = fields.Many2many('subject.subject', 'subject_hcp_rel',
                                  'hcp_id', 'subject_id', 'Course-Subjects',
                                  help='Select subject of hcp')
    podiatry_id = fields.Many2one('podiatry.podiatry', "Campus",
                                  help='Select podiatry')
    category_ids = fields.Many2many('hr.employee.category',
                                    'hcp_category_rel', 'emp_id', 'categ_id', 'Tags',
                                    help='Select employee category')
    department_id = fields.Many2one('hr.department', 'Department',
                                    help='Select department')
    is_doctor = fields.Boolean('Is doctor',
                               help='Select this if it doctor')
    pt_doctor_id = fields.Many2one('podiatry.doctor', 'Related doctor',
                                   help='Enter patient doctor')
    patient_id = fields.Many2many('patient.patient',
                                  'patients_hcps_doctor_rel', 'hcp_id', 'patient_id',
                                  'Children', help='Select patient')
    phone_numbers = fields.Char("Phone Number", help='Patient PH no')

    @api.onchange('standard_id')
    def _onchange_standard_id(self):
        for rec in self:
            rec.podiatry_id = (rec.standard_id and rec.standard_id.podiatry_id and
                               rec.standard_id.podiatry_id.id or False)

    @api.onchange('is_doctor')
    def _onchange_is_doctor(self):
        """Onchange method for is doctor"""
        self.pt_doctor_id = False
        self.patient_id = False

    @api.model
    def create(self, vals):
        """Inherited create method to assign value to users for delegation"""
        hcp_id = super(PodiatryHCP, self).create(vals)
        user_obj = self.env['res.users']
        user_vals = {'name': hcp_id.name,
                     'login': hcp_id.work_email,
                     'email': hcp_id.work_email,
                     }
        ctx_vals = {'hcp_create': True,
                    'podiatry_id': hcp_id.podiatry_id.company_id.id}
        user_rec = user_obj.with_context(ctx_vals).create(user_vals)
        hcp_id.employee_id.write({'user_id': user_rec.id})
#        if vals.get('is_doctor'):
#            self.doctor_crt(hcp_id)
        return hcp_id

# Removing this code because of issue faced due to email id of the
# user is same for doctor and HCP, and system will not allow it.
# now user shuld create doctor record first and then select it in
# related doctor in HCP Profile. - Anu Patel (24/03/2021)
#    def doctor_crt(self, manager_id):
#        """Method to create doctor record based on doctor field"""
#        pt_doctor = []
#        if manager_id.pt_doctor_id:
#            pt_doctor = manager_id.pt_doctor_id
#        if not pt_doctor:
#            emp_user = manager_id.employee_id
#            patients = [pt.id for pt in manager_id.patient_id]
#            doctor_vals = {'name': manager_id.name,
#                           'email': emp_user.work_email,
#                           'user_ids': [(6, 0, [emp_user.user_id.id])],
#                           'partner_id': emp_user.user_id.partner_id.id,
#                           'patient_id': [(6, 0, patients)]}
#            pt_doctor = self.env['podiatry.doctor'].with_context().create(doctor_vals)
#            manager_id.write({'pt_doctor_id': pt_doctor.id})
#        user = pt_doctor.user_ids
#        user_rec = user[0]
#        doctor_grp_id = self.env.ref('podiatry.group_podiatry_doctor')
#        groups = doctor_grp_id
#        if user_rec.groups_id:
#            groups = user_rec.groups_id
#            groups += doctor_grp_id
#        group_ids = [group.id for group in groups]
#        user_rec.write({'groups_id': [(6, 0, group_ids)]})

    def write(self, vals):
        """Inherited write method to assign groups based on doctor field"""
        # if vals.get('is_doctor'):
        #     self.doctor_crt(self)
        if vals.get('patient_id'):
            self.pt_doctor_id.write({'patient_id': vals.get('patient_id')})
        if not vals.get('is_doctor'):
            user_rec = self.employee_id.user_id
            doctor_grp_id = self.env.ref('podiatry.group_podiatry_doctor')
            groups = doctor_grp_id
            if doctor_grp_id in user_rec.groups_id:
                user_rec.write({'groups_id': [(3, doctor_grp_id.id)]})
        return super(PodiatryHCP, self).write(vals)

    @api.onchange('address_id')
    def onchange_address_id(self):
        """Onchange method for address."""
        if self.address_id:
            self.work_phone = self.address_id.phone or False,
            self.mobile_phone = self.address_id.mobile or False

    @api.onchange('department_id')
    def onchange_department_id(self):
        """Onchange method for deepartment."""
        self.doctor_id = (self.department_id and
                          self.department_id.manager_id and
                          self.department_id.manager_id.id) or False

    @api.onchange('user_id')
    def onchange_user(self):
        """Onchange method for user."""
        if self.user_id:
            self.name = self.name or self.user_id.name
            self.work_email = self.user_id.email
            self.image = self.image or self.user_id.image

    @api.onchange('podiatry_id')
    def onchange_podiatry(self):
        """Onchange method for podiatry."""
        partner = self.podiatry_id.company_id.partner_id
        self.address_id = partner.id or False
        self.mobile_phone = partner.mobile or False
        self.work_location_id = partner.id or False
        self.work_email = partner.email or False
        phone = partner.phone or False
        self.work_phone = phone or False
        self.phone_numbers = phone or False
