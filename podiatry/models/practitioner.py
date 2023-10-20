# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PodiatryPractitioner(models.Model):
    """Defining a Practitioner information."""

    _name = "podiatry.practitioner"
    _description = "Practitioner Information"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    partner_id = fields.Many2one(
        "res.partner",
        "Partner ID",
        ondelete="cascade",
        delegate=True,
        required=True,
        help="Enter related partner",
    )
    
    child_ids = fields.One2many('hr.employee', 'parent_id', string='Direct subordinates')
    
    user_id = fields.Many2one('res.users', 'User', related='resource_id.user_id', store=True, readonly=False)
    user_partner_id = fields.Many2one(related='user_id.partner_id', related_sudo=False, string="User's partner")
    active = fields.Boolean('Active', related='resource_id.active', default=True, store=True, readonly=False)
    company_id = fields.Many2one('res.company',required=True)
    
    practice_id = fields.Many2one("podiatry.practice", "Practice", help="Select a practice")
    
    address_id = fields.Many2one(
        'res.partner', string='Address', default=lambda self: self.env.company.partner_id.id,
        tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    
    standard_id = fields.Many2one(
        "podiatry.standard",
        "Responsibility of Academic Class",
        help="Standard for which the practitioner responsible for.",
    )
    stand_id = fields.Many2one(
        "standard.standard",
        "Course",
        related="standard_id.standard_id",
        store=True,
        help="""Select standard which are assigned to practitioner""",
    )
    subject_id = fields.Many2many(
        "subject.subject",
        "subject_practitioner_rel",
        "practitioner_id",
        "subject_id",
        "Course-Subjects",
        help="Select subject of practitioner",
    )

   
    
    function = fields.Char(string='Job Position')
    # practice_id = fields.Many2one(
    #     'podiatry.practice', 
    #     required=True, 
    #     index=True, 
    #     domain=[('is_company','=',True)], 
    #     string="Practice"
    #     )
    
    # def _default_category(self):
    #     return self.env['res.partner.category'].browse(self._context.get('category_id'))
    notes = fields.Text('Notes', groups="base.group_user")

    category_ids = fields.Many2many(
        "res.partner.category",
        "practitioner_category_rel",
        "partner_id",
        "categ_id",
        "Tags",
        help="Select partner category",
    )
    # category_id = fields.Many2many('res.partner.category', column1='partner_id',
    #                                 column2='category_id', string='Tags', default=_default_category)
    location_id = fields.Many2one("base.department", "Department", help="Select department")
    
    location_ids = fields.One2many("res.partner", compute="_compute_locations", string="Locations", readonly=True)

    # function = fields.Char(string='Job Position')
    is_doctor = fields.Boolean("Is Doctor", help="Select this if it doctor")
    pat_doctor_id = fields.Many2one(
        "podiatry.doctor", "Related Doctor", help="Enter patient doctor"
    )
    patient_id = fields.Many2many(
        "patient.patient",
        "patients_practitioners_doctor_rel",
        "practitioner_id",
        "patient_id",
        "Children",
        help="Select patient",
    )

    @api.onchange("standard_id")
    def _onchange_standard_id(self):
        for rec in self:
            rec.practice_id = (
                rec.standard_id
                and rec.standard_id.practice_id
                and rec.standard_id.practice_id.id
                or False
            )

    @api.onchange("is_doctor")
    def _onchange_isdoctor(self):
        """Onchange method for is doctor"""
        self.pat_doctor_id = False
        self.patient_id = False

    @api.model
    def create(self, vals):
        """Inherited create method to assign value to partners for delegation"""
        practitioner_id = super(PodiatryPractitioner, self).create(vals)
        partner_obj = self.env["res.partner"]
        partner_vals = {
            "name": practitioner_id.name,
            "login": practitioner_id.email,
            "email": practitioner_id.email,
        }
        ctx_vals = {
            "practitioner_create": True,
            "practice_id": practitioner_id.practice_id.company_id.id,
        }
        partner_rec = partner_obj.with_context(ctx_vals).create(partner_vals)
        practitioner_id.partner_id.write({"partner_id": partner_rec.id})
        #        if vals.get('is_doctor'):
        #            self.doctor_crt(practitioner_id)
        return practitioner_id

    # Removing this code because of issue faced due to email id of the
    # partner is same for doctor and Practitioner, and system will not allow it.
    # now partner shuld create Doctor record first and then select it in
    # related doctor in Practitioner Profile. - Anu Patel (24/03/2021)
    #    def doctor_crt(self, manager_id):
    #        """Method to create doctor record based on doctor field"""
    #        pat_doctor = []
    #        if manager_id.pat_doctor_id:
    #            pat_doctor = manager_id.pat_doctor_id
    #        if not pat_doctor:
    #            emp_partner = manager_id.partner_id
    #            patients = [pat.id for pat in manager_id.patient_id]
    #            doctor_vals = {'name': manager_id.name,
    #                           'email': emp_partner.email,
    #                           'child_ids': [(6, 0, [emp_partner.partner_id.id])],
    #                           'partner_id': emp_partner.partner_id.partner_id.id,
    #                           'patient_id': [(6, 0, patients)]}
    #            pat_doctor = self.env['podiatry.doctor'].with_context(
    #                       ).create(doctor_vals)
    #            manager_id.write({'pat_doctor_id': pat_doctor.id})
    #        partner = pat_doctor.child_ids
    #        partner_rec = partner[0]
    #        doctor_grp_id = self.env.ref('podiatry.group_podiatry_doctor')
    #        groups = doctor_grp_id
    #        if partner_rec.groups_id:
    #            groups = partner_rec.groups_id
    #            groups += doctor_grp_id
    #        group_ids = [group.id for group in groups]
    #        partner_rec.write({'groups_id': [(6, 0, group_ids)]})

    def write(self, vals):
        """Inherited write method to assign groups based on doctor field"""
        # if vals.get('is_doctor'):
        #     self.doctor_crt(self)
        if vals.get("patient_id"):
            self.pat_doctor_id.write({"patient_id": vals.get("patient_id")})
        if not vals.get("is_doctor"):
            partner_rec = self.partner_id
            doctor_grp_id = self.env.ref("podiatry.group_podiatry_doctor")
            if doctor_grp_id in partner_rec.groups_id:
                partner_rec.write({"groups_id": [(3, doctor_grp_id.id)]})
        return super(PodiatryPractitioner, self).write(vals)

    @api.onchange("address_id")
    def onchange_address_id(self):
        """Onchange method for address."""
        if self.address_id:
            self.phone = (self.address_id.phone or False,)
            self.mobile = self.address_id.mobile or False

    @api.onchange("location_id")
    def onchange_location_id(self):
        """Onchange method for deepartment."""
        self.doctor_id = (
            self.location_id
            and self.location_id.manager_id
            and self.location_id.manager_id.id
        ) or False

    @api.onchange("partner_id")
    def onchange_partner(self):
        """Onchange method for partner."""
        if self.partner_id:
            self.name = self.name or self.partner_id.name
            self.email = self.partner_id.email
            self.image = self.image or self.partner_id.image

    @api.onchange("practice_id")
    def onchange_podiatry(self):
        """Onchange method for podiatry."""
        partner = self.practice_id.company_id.partner_id
        self.address_id = partner.id or False
        self.mobile = partner.mobile or False
        self.location_id = partner.id or False
        self.email = partner.email or False
        phone = partner.phone or False
        self.phone = phone or False

