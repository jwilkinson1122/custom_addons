# -*- coding: utf-8 -*-

from odoo import api, models


class PatientReport(models.AbstractModel):
    _name = 'report.km_hospital.report_patient_card'
    _description = 'Patient Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        docs = self.env['kmhospital.patient'].browse(docids)
        prescriptions = self.env['kmhospital.eprescription'].search(
            [("name", "=", docids)])
        prescription_list = []
        for eprescription in prescriptions:
            values = {
                "checkup_date": eprescription.checkup_date,
                "status": eprescription.status,
                "appointed_doctor_id": eprescription.appointed_doctor_id.name,
            }
            prescription_list.append(values)
        return {
            'doc_model': 'kmhospital.patient',
            'data': data,
            'docs': docs,
            'prescription_list': prescription_list,
        }
