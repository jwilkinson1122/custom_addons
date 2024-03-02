# -*- coding: utf-8 -*-


from odoo import api, fields, models


class PrescriptionTypeAssignationLog(models.Model):
    _name = "prescription.type.assignation.log"
    _description = "Practitioners history on a prescription"
    _order = "create_date desc, date_start desc"

    prescription_id = fields.Many2one('prescription.type', string="Prescription", required=True)
    location_id = fields.Many2one('res.partner', string="Practitioner", required=True)
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")

    @api.depends('location_id', 'prescription_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'{rec.prescription_id.name} - {rec.location_id.name}'
