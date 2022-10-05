from odoo import models, fields, api


class PractitionerPrescription(models.Model):
    _name = 'podiatry.practitioner.prescription'
    _description = 'Doctor Appointment'

    name = fields.Char()
    # readonly = True
    active = fields.Boolean(default=True)

    color = fields.Integer()

    date = fields.Date()
    time = fields.Datetime()

    practitioner_id = fields.Many2one(
        comodel_name='podiatry.practitioner',
        string='Doctor')

    patient_id = fields.Many2one(
        comodel_name='podiatry.patient',
        string='Patient')

    description = fields.Text(string='Description')

    diagnosis_id = fields.Many2one(
        comodel_name='podiatry.patient.diagnosis',
        string='diagnosis')

    # practitioner_id = fields.Many2one(
    #     comodel_name='podiatry.practitioner',
    #     inverse_name='practice_id',
    #     string="Diagnosis",
    # )

    @api.onchange('patient_id', 'practitioner_id', 'date')
    def _onchange_name(self):
        self.name = f'{self.patient_id.name} | {self.practitioner_id.name} ({self.date})'
