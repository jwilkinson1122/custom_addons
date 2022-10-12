# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SearchPrescriptionWizard(models.TransientModel):
    _name = "search.eprescription.wizard"
    _description = "Search E-Prescription Wizard"

    patient_id = fields.Many2one(
        'podiatry.patient', string="Patient", required=True)

    def action_search_prescription_m1(self):
        action = self.env.ref(
            'om_hospital.action_hospital_prescription').read()[0]
        action['domain'] = [('patient_id', '=', self.patient_id.id)]
        return action

    def action_search_prescription_m2(self):
        action = self.env['ir.actions.actions']._for_xml_id(
            "om_hospital.action_hospital_prescription")
        action['domain'] = [('patient_id', '=', self.patient_id.id)]
        return action

    def action_search_prescription_m3(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'podiatry.eprescription',
            'view_type': 'form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
