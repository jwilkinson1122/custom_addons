from odoo import fields, models, _, api


class PrescriptionReportWizard(models.TransientModel):
    _name = 'prescription.report.wizard'
    _description = 'Prescriptions Report Wizard'

    patient_id = fields.Many2one('hospital.patient', string="Patient")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")

    def action_prescription_report(self):
        domain = []
        patient_id = self.patient_id
        if patient_id:
            domain += [('patient_id', '=', patient_id.id)]

        date_from = self.date_from
        if date_from:
            domain += [('date_prescription', '>=', date_from)]

        date_to = self.date_to
        if date_to:
            domain += [('date_prescription', '<=', date_to)]

        print (domain)
        prescriptions = self.env['hospital.prescription'].search_read(domain)
        data = {
            'form_data': self.read()[0],
            'prescriptions': prescriptions
        }
        print(self.read()[0])
        return self.env.ref('om_hospital.action_report_patient_prescriptions').report_action(self, data=data)

