# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class DoctorRelation(models.Model):
    """Defining a Doctor relation with child."""

    _name = "doctor.relation"
    _description = "Doctor-child relation information"

    name = fields.Char(
        "Relation name", required=True, help="Doctor relation with patient"
    )


class PodiatryDoctor(models.Model):
    """Defining a Practitioner information."""

    _name = "podiatry.doctor"
    _description = "Doctor Information"

    partner_id = fields.Many2one(
        "res.partner",
        "Partner ID",
        ondelete="cascade",
        delegate=True,
        required=True,
        help="Partner which is partner over here",
    )
    relation_id = fields.Many2one(
        "doctor.relation",
        "Relation with Child",
        help="Doctor relation with child",
    )
    patient_id = fields.Many2many(
        "patient.patient",
        "patients_doctors_rel",
        "patients_doctor_id",
        "patient_id",
        "Children",
        help="Patient of the following doctor",
    )
    standard_id = fields.Many2many(
        "podiatry.standard",
        "podiatry_standard_doctor_rel",
        "class_doctor_id",
        "class_id",
        "Academic Class",
        help="""Class of the patient of following doctor""",
    )
    stand_id = fields.Many2many(
        "standard.standard",
        "standard_standard_doctor_rel",
        "standard_doctor_id",
        "standard_id",
        "Academic Standard",
        help="""Standard of the patient of following doctor""",
    )
    practitioner_id = fields.Many2one(
        "podiatry.practitioner",
        "Practitioner",
        store=True,
        related="standard_id.partner_id",
        help="Practitioner of a patient",
    )

    @api.onchange("patient_id")
    def onchange_patient_id(self):
        """Onchange Method for Patient."""
        standard_ids = self.patient_id.mapped("standard_id")
        if standard_ids:
            self.standard_id = [(6, 0, standard_ids.ids)]
            self.stand_id = [(6, 0, standard_ids.mapped("standard_id").ids)]

    @api.model
    def create(self, vals):
        """Inherited create method to assign values in
        the partners record to maintain the delegation"""
        res = super(PodiatryDoctor, self).create(vals)
        doctor_grp_id = self.env.ref("podiatry.group_podiatry_doctor")
        partner_grp = self.env.ref("base.group_user")
        self.env["res.partner"].create(
            {
                "name": res.name,
                "login": res.email,
                "email": res.email,
                "partner_id": res.partner_id.id,
                "groups_id": [(6, 0, [partner_grp.id, doctor_grp_id.id])],
            }
        )
        return res

    @api.onchange("state_id")
    def onchange_state(self):
        """Onchange Method for State."""
        if self.state_id:
            self.country_id = self.state_id.country_id.id or False
