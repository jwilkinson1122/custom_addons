# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import date, datetime


class podiatry_patient_registration(models.Model):
    _name = 'podiatry.patient.registration'
    _description = 'Podiatry Patient Registration'

    name = fields.Char(string="Registration Code",
                       copy=False, readonly=True, index=True)
    patient_id = fields.Many2one(
        'podiatry.patient', string="Patient", required=True)
    care_date = fields.Datetime(
        string="Care date", required=True)
    primary_physician_id = fields.Many2one(
        'podiatry.physician', string="Primary Physician")
    podiatry_pathology_id = fields.Many2one(
        'podiatry.pathology', string="Medical Pathology")
    info = fields.Text(string="Extra Info")
    location_transfers_ids = fields.One2many(
        'location.transfer', 'patient_id', string='Transfer Location', readonly=True)
    state = fields.Selection([('free', 'Free'), ('confirmed', 'Confirmed'), (
        'cancel', 'Cancel'), ('done', 'Done')], string="State", default="free")
    device_ids = fields.One2many(
        'podiatry.patient.device', 'podiatry_patient_registration_id', string='Device')

    @api.model
    def default_get(self, fields):
        result = super(podiatry_patient_registration,
                       self).default_get(fields)
        patient_id = self.env['ir.sequence'].next_by_code(
            'podiatry.patient.registration')
        if patient_id:
            result.update({
                'name': patient_id,
            })
        return result

    def registration_confirm(self):
        self.write({'state': 'confirmed'})

    def registration_cancel(self):
        self.write({'state': 'cancel'})

    def patient_discharge(self):
        self.write({'state': 'done'})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
