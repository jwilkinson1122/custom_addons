# -*- coding: utf-8 -*-

from odoo import api, models


class PatientReport(models.AbstractModel):
    _name = 'report.pod_manager.report_patient_card'
    _description = 'Patient Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        docs = self.env['pod.manager.patient'].browse(docids)
        prescriptions = self.env['pod.manager.prescription'].search(
            [("name", "=", docids)])
        prescription_list = []
        for prescription in prescriptions:
            values = {
                "requested_date": prescription.requested_date,
                "status": prescription.status,
                "appointed_doctor_id": prescription.appointed_doctor_id.name,
            }
            prescription_list.append(values)
        return {
            'doc_model': 'pod.manager.patient',
            'data': data,
            'docs': docs,
            'prescription_list': prescription_list,
        }
