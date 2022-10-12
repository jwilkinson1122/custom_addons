# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CreatePrescriptionWizard(models.TransientModel):
    _name = "create.eprescription.wizard"
    _description = "Create E-Prescription Wizard"

    @api.model
    def default_get(self, fields):
        res = super(CreatePrescriptionWizard, self).default_get(fields)
        if self._context.get('active_id'):
            res['patient_id'] = self._context.get('active_id')
        return res

    date_prescription = fields.Date(string='Date', required=False)
    patient_id = fields.Many2one(
        'podiatry.patient', string="Patient", required=True)

    def action_create_prescription(self):
        vals = {
            'patient_id': self.patient_id.id,
            'doctor_id': 2,
            'date_prescription': self.date_prescription
        }
        prescription_rec = self.env['podiatry.eprescription'].create(vals)
        return {
            'name': _('E-Prescription'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'podiatry.eprescription',
            'res_id': prescription_rec.id,
        }

    # def action_view_prescription(self):
    #     # action = self.env.ref('om_hospital.action_hospital_prescription').read()[0]
    #     # action['domain'] = [('patient_id', '=', self.patient_id.id)]
    #     # return action
    #
    #     action = self.env['ir.actions.actions']._for_xml_id("om_hospital.action_hospital_prescription")
    #     action['domain'] = [('patient_id', '=', self.patient_id.id)]
    #     return action
    #
    #     # return {
    #     #     'type': 'ir.actions.act_window',
    #     #     'name': 'Prescriptions',
    #     #     'res_model': 'podiatry.eprescription',
    #     #     'view_type': 'form',
    #     #     'domain': [('patient_id', '=', self.patient_id.id)],
    #     #     'view_mode': 'tree,form',
    #     #     'target': 'current',
    #     # }
    #     # return action
