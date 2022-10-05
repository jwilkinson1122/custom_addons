from odoo import models, fields, api


class PractitionerHistory(models.Model):
    _name = 'podiatry.personal.practitioner.history'
    _description = 'Podiatry personal_practitioner_history'

    name = fields.Char()
    active = fields.Boolean(default=True)

    # (date of diagnosis)
    date = fields.Date()

    # (practitioner)
    practitioner_id = fields.Many2one(
        comodel_name='podiatry.practitioner',
        string='Practitioner')

    # patient
    patient_id = fields.Many2one(
        comodel_name='podiatry.patient',
        string='patient')

    @api.onchange('patient_id', 'practitioner_id', 'practitioner_id', 'date')
    def _onchange_name(self):
        self.name = f'{self.patient_id.name} | {self.practitioner_id.name} ({self.date})'
