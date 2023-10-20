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
except Exception:
    image_colorize = False


class PatientPatient(models.Model):
    """Defining a patient information."""

    _name = "patient.patient"
    _table = "patient_patient"
    _description = "Patient Information"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        """Method to get patient of doctor having group practitioner"""
        practitioner_group = self.env.user.has_group("podiatry.group_podiatry_practitioner")
        doctor_grp = self.env.user.has_group("podiatry.group_podiatry_doctor")
        login_partner_rec = self.env.user
        name = self._context.get("patient_id")
        if name and practitioner_group and doctor_grp:
            doctor_login_patient_rec = self.env["podiatry.doctor"].search(
                [("partner_id", "=", login_partner_rec.partner_id.id)]
            )
            childrens = doctor_login_patient_rec.patient_id
            args.append(("id", "in", childrens.ids))
        return super(PatientPatient, self)._search(
            args=args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )

    @api.depends("date_of_birth")
    def _compute_patient_age(self):
        """Method to calculate patient age"""
        current_dt = fields.Date.today()
        for rec in self:
            rec.age = 0
            if rec.date_of_birth and rec.date_of_birth < current_dt:
                start = rec.date_of_birth
                age_calc = (current_dt - start).days / 365
                # Age should be greater than 0
                if age_calc > 0.0:
                    rec.age = age_calc

    @api.model
    def _default_image(self):
        """Method to get default Image"""
        image_path = get_module_resource(
            "hr", "static/src/img", "default_image.png"
        )
        return base64.b64encode(open(image_path, "rb").read())

    @api.depends("state")
    def _compute_practitioner_partner(self):
        """Compute practitioner boolean field if partner form practitioner group"""
        practitioner = self.env.user.has_group("podiatry.group_podiatry_practitioner")
        for rec in self:
            rec.practitioner_partner_grp = False
            if practitioner and rec.state == "done":
                rec.practitioner_partner_grp = True

    @api.model
    def check_current_year(self):
        """Method to get default value of logged in Patient"""
        res = self.env["academic.year"].search([("current", "=", True)])
        if not res:
            raise ValidationError(
                _(
                    "There is no current Academic Year defined! Please "
                    "contact Administator!"
                )
            )
        return res.id

    patient_contact_ids = fields.One2many(
        "patient.contact",
        "patient_contact_id",
        "Patient Contact Detail",
        states={"done": [("readonly", True)]},
        help="Select the patient contact",
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Partner ID",
        ondelete="cascade",
        required=True,
        delegate=True,
        help="Select related partner of the patient",
    )
    patient_name = fields.Char(
        "Patient Name",
        related="partner_id.name",
        store=True,
        readonly=True,
        help="Patient Name",
    )
    pid = fields.Char(
        "Patient ID",
        required=True,
        default=lambda self: _("New"),
        help="Personal IDentification Number",
    )
    reg_code = fields.Char(
        "Registration Code", help="Patient Registration Code"
    )
    patient_code = fields.Char("Patient Code", help="Enter patient code")
    contact_phone = fields.Char("Phone no.", help="Enter patient phone no.")
    contact_mobile = fields.Char("Mobile no", help="Enter patient mobile no.")
    roll_no = fields.Integer(
        "Roll No.", readonly=True, help="Enter patient roll no."
    )
    photo = fields.Binary(
        "Photo", default=_default_image, help="Attach patient photo"
    )
    year = fields.Many2one(
        "academic.year",
        "Academic Year",
        readonly=True,
        default=check_current_year,
        help="Select academic year",
        tracking=True,
    )
    cast_id = fields.Many2one(
        "patient.cast", "Religion/Caste", help="Select patient cast"
    )
    relation = fields.Many2one(
        "patient.relation.master", "Relation", help="Select patient relation"
    )

    admission_date = fields.Date(
        "Admission Date",
        default=fields.Date.today(),
        help="Enter patient admission date",
    )
    middle = fields.Char(
        "Middle Name",
        required=True,
        states={"done": [("readonly", True)]},
        help="Enter patient middle name",
    )
    last = fields.Char(
        "Surname",
        required=True,
        states={"done": [("readonly", True)]},
        help="Enter patient last name",
    )
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female")],
        "Gender",
        states={"done": [("readonly", True)]},
        help="Select patient gender",
    )
    date_of_birth = fields.Date(
        "BirthDate",
        required=True,
        states={"done": [("readonly", True)]},
        help="Enter patient date of birth",
    )
    mother_tongue = fields.Many2one(
        "mother.toungue", "Mother Tongue", help="Select patient mother tongue"
    )
    age = fields.Integer(
        compute="_compute_patient_age",
        string="Age",
        readonly=True,
        help="Enter patient age",
    )
    maritual_status = fields.Selection(
        [("unmarried", "Unmarried"), ("married", "Married")],
        "Marital Status",
        states={"done": [("readonly", True)]},
        help="Select patient maritual status",
    )
    reference_ids = fields.One2many(
        "patient.reference",
        "reference_id",
        "References",
        states={"done": [("readonly", True)]},
        help="Enter patient references",
    )
    previous_practice_ids = fields.One2many(
        "patient.previous.podiatry",
        "previous_practice_id",
        "Previous Podiatry Detail",
        states={"done": [("readonly", True)]},
        help="Enter patient podiatry details",
    )
    doctor = fields.Char(
        "Doctor Name",
        states={"done": [("readonly", True)]},
        help="Enter doctor name for patient medical details",
    )
    designation = fields.Char("Designation", help="Enter doctor designation")
    doctor_phone = fields.Char("Contact No.", help="Enter doctor phone")
    blood_group = fields.Char("Blood Group", help="Enter patient blood group")
    height = fields.Float("Height", help="Hieght in C.M")
    weight = fields.Float("Weight", help="Weight in K.G")
    eye = fields.Boolean("Eyes", help="Eye for medical info")
    ear = fields.Boolean("Ears", help="Eye for medical info")
    nose_throat = fields.Boolean(
        "Nose & Throat", help="Nose & Throat for medical info"
    )
    respiratory = fields.Boolean(
        "Respiratory", help="Respiratory for medical info"
    )
    cardiovascular = fields.Boolean(
        "Cardiovascular", help="Cardiovascular for medical info"
    )
    neurological = fields.Boolean(
        "Neurological", help="Neurological for medical info"
    )
    muskoskeletal = fields.Boolean(
        "Musculoskeletal", help="Musculoskeletal for medical info"
    )
    dermatological = fields.Boolean(
        "Dermatological", help="Dermatological for medical info"
    )
    blood_pressure = fields.Boolean(
        "Blood Pressure", help="Blood pressure for medical info"
    )
    remark = fields.Text(
        "Remark",
        states={"done": [("readonly", True)]},
        help="Remark can be entered if any",
    )
    practice_id = fields.Many2one(
        "podiatry.practice",
        "Podiatry",
        states={"done": [("readonly", True)]},
        help="Select podiatry",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
            ("close", "Close"),
            ("cancel", "Cancel"),
            ("alumni", "Alumni"),
        ],
        "Status",
        readonly=True,
        default="draft",
        tracking=True,
        help="State of the patient registration form",
    )
    history_ids = fields.One2many(
        "patient.history",
        "patient_id",
        "History",
        help="Enter patient history",
    )
    certificate_ids = fields.One2many(
        "patient.certificate",
        "patient_id",
        "Certificate",
        help="Enter patient certificates",
    )
    patient_discipline_line = fields.One2many(
        "patient.descipline",
        "patient_id",
        "Descipline",
        help="""Enter patient descipline info""",
    )
    document = fields.One2many(
        "patient.document",
        "doc_id",
        "Documents",
        help="Attach patient documents",
    )
    description = fields.One2many(
        "patient.description", "des_id", "Description", help="Description"
    )
    award_list = fields.One2many(
        "patient.award",
        "award_list_id",
        "Award List",
        help="Patient award list",
    )
    pat_name = fields.Char(
        "First Name",
        related="partner_id.name",
        readonly=True,
        help="Enter patient first name",
        tracking=True,
    )
    Acadamic_year = fields.Char(
        "Year",
        related="year.name",
        help="Academic Year",
        readonly=True,
        tracking=True,
    )
    division_id = fields.Many2one(
        "standard.division",
        "Division",
        help="Select patient standard division",
        tracking=True,
    )
    medium_id = fields.Many2one(
        "standard.medium",
        "Medium",
        help="Select patient standard medium",
        tracking=True,
    )
    standard_id = fields.Many2one(
        "podiatry.standard",
        "Class",
        help="Select patient standard",
        tracking=True,
    )
    doctor_id = fields.Many2many(
        "podiatry.doctor",
        "patients_doctors_rel",
        "patient_id",
        "patients_doctor_id",
        "Doctor(s)",
        states={"done": [("readonly", True)]},
        help="Enter patient doctors",
    )
    close_reason = fields.Text(
        "Reason", help="Enter patient close reason", tracking=True
    )
    active = fields.Boolean(
        default=True, help="Activate/Deactivate patient record", tracking=True
    )
    practitioner_partner_grp = fields.Boolean(
        "Practitioner Group",
        compute="_compute_practitioner_partner",
        help="Activate/Deactivate practitioner group",
    )

    @api.model
    def create(self, vals):
        """Method to create partner when patient is created"""
        if vals.get("pid", _("New")) == _("New"):
            vals["pid"] = self.env["ir.sequence"].next_by_code(
                "patient.patient"
            ) or _("New")
        if vals.get("pid", False):
            vals["login"] = vals["pid"]
            vals["password"] = vals["pid"]
        else:
            raise UserError(
                _("Error! PID not valid so record will not be saved.")
            )
        if vals.get("company_id", False):
            company_vals = {"company_ids": [(4, vals.get("company_id"))]}
            vals.update(company_vals)
        if vals.get("email"):
            podiatry.emailvalidation(vals.get("email"))
        res = super(PatientPatient, self).create(vals)
        practitioner = self.env["podiatry.practitioner"]
        for data in res.doctor_id:
            for record in practitioner.search([("pat_doctor_id", "=", data.id)]):
                record.write({"patient_id": [(4, res.id, None)]})
        # Assign group to patient based on condition
        partner_grp = self.env.ref("base.group_user")
        if res.state == "draft":
            admission_group = self.env.ref("podiatry.group_is_admission")
            new_grp_list = [admission_group.id, partner_grp.id]
            res.partner_id.write({"groups_id": [(6, 0, new_grp_list)]})
        elif res.state == "done":
            done_patient = self.env.ref("podiatry.group_podiatry_patient")
            group_list = [done_patient.id, partner_grp.id]
            res.partner_id.write({"groups_id": [(6, 0, group_list)]})
        return res

    def write(self, vals):
        """Inherited method write to assign
        patient to their respective practitioner"""
        practitioner = self.env["podiatry.practitioner"]
        if vals.get("doctor_id"):
            for doctor in vals.get("doctor_id")[0][2]:
                for data in practitioner.search([("pat_doctor_id", "=", doctor)]):
                    data.write({"patient_id": [(4, self.id)]})
        return super(PatientPatient, self).write(vals)

    @api.constrains("date_of_birth")
    def check_age(self):
        """Method to check age should be greater than 6"""
        if self.date_of_birth:
            start = self.date_of_birth
            age_calc = (fields.Date.today() - start).days / 365
            # Check if age less than required age
            if age_calc < self.practice_id.required_age:
                raise ValidationError(
                    _(
                        "Age of patient should be greater than %s years!"
                        % (self.practice_id.required_age)
                    )
                )

    def set_to_draft(self):
        """Method to change state to draft"""
        self.state = "draft"

    def set_alumni(self):
        """Method to change state to alumni"""
        for rec in self:
            rec.state = "alumni"
            rec.standard_id._compute_total_patient()
            rec.active = False
            rec.partner_id.active = False

    def set_done(self):
        """Method to change state to done"""
        self.state = "done"

    def admission_draft(self):
        """Set the state to draft"""
        self.state = "draft"

    def set_close(self):
        """Set the state to close"""
        self.state = "close"

    def cancel_admission(self):
        """Set the state to cancel."""
        self.state = "cancel"

    def admission_done(self):
        """Method to confirm admission"""
        podiatry_standard_obj = self.env["podiatry.standard"]
        ir_sequence = self.env["ir.sequence"]
        patient_group = self.env.ref("podiatry.group_podiatry_patient")
        partner_group = self.env.ref("base.group_user")
        for rec in self:
            if not rec.standard_id:
                raise ValidationError(_("Please select class!"))
            if rec.standard_id.remaining_seats <= 0:
                raise ValidationError(
                    _("Seats of class %s are full")
                    % rec.standard_id.standard_id.name
                )
            domain = [("practice_id", "=", rec.practice_id.id)]
            # Checks the standard if not defined raise error
            if not podiatry_standard_obj.search(domain):
                raise UserError(
                    _("Warning! The standard is not defined in podiatry!")
                )
            # Assign group to patient
            rec.partner_id.write(
                {"groups_id": [(6, 0, [partner_group.id, patient_group.id])]}
            )
            # Assign roll no to patient
            number = 1
            for rec_std in rec.search(domain):
                rec_std.roll_no = number
                number += 1
            # Assign registration code to patient
            reg_code = ir_sequence.next_by_code("patient.registration")
            registation_code = (
                str(rec.practice_id.state_id.name)
                + str("/")
                + str(rec.practice_id.city)
                + str("/")
                + str(rec.practice_id.name)
                + str("/")
                + str(reg_code)
            )
            pat_code = ir_sequence.next_by_code("patient.code")
            patient_code = (
                str(rec.practice_id.code)
                + str("/")
                + str(rec.year.code)
                + str("/")
                + str(pat_code)
            )
            rec.write(
                {
                    "state": "done",
                    "admission_date": fields.Date.today(),
                    "patient_code": patient_code,
                    "reg_code": registation_code,
                }
            )
            template = (
                self.env["mail.template"]
                .sudo()
                .search([("name", "ilike", "Admission Confirmation")], limit=1)
            )
            if template:
                for partner in rec.doctor_id:
                    subject = _("About Admission Confirmation")
                    if partner.email:
                        body = (
                            """
                        <div>
                            <p>Dear """
                            + str(partner.display_name)
                            + """,
                            <br/><br/>
                            Admission of """
                            + str(rec.display_name)
                            + """ has been confirmed in """
                            + str(rec.practice_id.name)
                            + """.
                            <br></br>
                            Thank You.
                        </div>
                        """
                        )
                        template.send_mail(
                            rec.id,
                            email_values={
                                "email_from": self.env.user.email or "",
                                "email_to": partner.email,
                                "subject": subject,
                                "body_html": body,
                            },
                            force_send=True,
                        )
        return True
