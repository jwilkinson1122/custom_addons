# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ArchiveReason(models.TransientModel):
    """Defining TransientModel to delete reason."""

    _name = "delete.reason"
    _description = "Archive Reason"

    reason = fields.Text('Reason')

    def save_delete(self):
        '''Method to delete patient and change state to delete.'''
        patient_rec = self.env['patient.patient'
                               ].browse(self._context.get('active_id'))
        patient_rec.write({'state': 'delete',
                           'delete_reason': self.reason,
                           'active': False})
        patient_rec.standard_id._compute_total_patient()
        for rec in self.env['patient.reminder'].search([
                ('pt_id', '=', patient_rec.id)]):
            rec.active = False
        if patient_rec.user_id:
            patient_rec.user_id.active = False
