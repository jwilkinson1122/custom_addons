# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AssignRollNo(models.TransientModel):
    '''designed for assigning roll number to a patient'''

    _name = 'assign.roll.no'
    _description = 'Assign Roll Number'

    practice_id = fields.Many2one(
        'podiatry.practice', 'Practice Location', required=True)

    def assign_rollno(self):
        '''Method to assign roll no to patients'''
        patient_obj = self.env['patient.patient']
        # Search Patient
        for rec in self:
            # Assign roll no according to name.
            number = 1
            for patient in patient_obj.search([
                ('practice_id', '=', rec.practice_id.id)],
                    order="name"):
                patient.write({'roll_no': number})
                number += 1
