# -*- coding: utf-8 -*-


from odoo import api, fields, models


class PrescriptionTypeMeasure(models.Model):
    _name = 'prescription.type.measure'
    _description = 'Measure log for a prescription'
    _order = 'date desc'

    name = fields.Char(compute='_compute_prescription_log_name', store=True)
    date = fields.Date(default=fields.Date.context_today)
    value = fields.Float('Measures Value', group_operator="max")
    prescription_id = fields.Many2one('prescription.type', 'Prescription', required=True)
    unit = fields.Selection(related='prescription_id.laterality', string="Unit", readonly=True)
    location_id = fields.Many2one(related="prescription_id.location_id", string="Practitioner", readonly=False)

    @api.depends('prescription_id', 'date')
    def _compute_prescription_log_name(self):
        for record in self:
            name = record.prescription_id.name
            if not name:
                name = str(record.date)
            elif record.date:
                name += ' / ' + str(record.date)
            record.name = name

    @api.onchange('prescription_id')
    def _onchange_prescription(self):
        if self.prescription_id:
            self.unit = self.prescription_id.laterality
