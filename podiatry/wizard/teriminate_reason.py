# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class TerminateReason(models.TransientModel):
    """Defining TransientModel to terminate reason."""

    _name = "terminate.reason"
    _description = "Terminate Reason"

    reason = fields.Text('Reason')

    def save_terminate(self):
        '''Method to terminate patient and change state to terminate.'''
        patient_rec = self.env['patient.patient'
                               ].browse(self._context.get('active_id'))
        patient_rec.write({'state': 'terminate',
                           'terminate_reason': self.reason,
                           'active': False})
        patient_rec.standard_id._compute_total_patient()
        for rec in self.env['patient.reminder'].search([
                ('pt_id', '=', patient_rec.id)]):
            rec.active = False
        if patient_rec.user_id:
            patient_rec.user_id.active = False
