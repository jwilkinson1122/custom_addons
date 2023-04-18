from odoo import fields, models


class HrHospitalSetDoctorForPatientsWizard(models.TransientModel):
    _name = 'cgu_hospital.set.doctor.wizard'
    _description = "Wizard to set_doctor_for_patients"

    patient_ids = fields.Many2many(
        string="patients",
        comodel_name='cgu_hospital.patient',
        relation='set_doctor_wizard_rel'
        # column2='patient_id'
        )

    doctor_id = fields.Many2one(
        comodel_name='cgu_hospital.doctor',
        string='Doctor')

    def action_set_personal_doctor(self):
        self.ensure_one()
        self.patient_ids.write({"personal_doctor_id": self.doctor_id.id})
