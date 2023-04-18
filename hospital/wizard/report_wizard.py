from odoo import fields, models, api


class PatientReportWizard(models.TransientModel):
    _name = 'hospital.patient.report.wizard'
    _description = 'hospital patient report wizard'

    patient_id = fields.Many2one(comodel_name='hospital.patient',
                                 string='Patient_id', required=False)
    from_date = fields.Datetime(string='From_date', required=False)
    to_date = fields.Datetime(string='To_date', required=False)

    def get_data(self):
        print("test".center(80, "#"))
        print(self.read()[0])
        query = """
            select 
            patient_name ,
            hospital_patient.id,
            count(patient_id) ,
            sum(age) 
            from hospital_patient, hospital_appointment
            where hospital_patient.id = hospital_appointment.patient_id 
            group by (patient_name,hospital_patient.id);
        """
        print()
        self.env.cr.execute(query)
        result = self.env.cr.fetchall()
        print(result)
        data = {
            'form': self.read()[0],
            'hassan': 5050,
            'q_result': result

        }
        return self.env.ref('hospital.wizard_report_patient').report_action(
            self, data=data)
