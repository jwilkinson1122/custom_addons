# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class MovePractices(models.TransientModel):
    """Defining TransientModel to move practice."""

    _name = 'move.practices'
    _description = "Move Practices"

    academic_year_id = fields.Many2one('academic.year', 'Year',
                                       required=True, help="""
The Acedemic year from which you need to move the patient to next Year.""")

    def move_start(self):
        '''Code for moving patient to next practice'''
        academic_obj = self.env['academic.year']
        podiatry_pract_obj = self.env['podiatry.practice']
        practice_obj = self.env["podiatry.account"]
        patient_obj = self.env['patient.patient']
        next_year_id = academic_obj.next_year(self.academic_year_id.sequence)
        if not next_year_id:
            raise ValidationError(_(
                """The next sequanced Acedemic year after the selected one is not configured!"""))
        done_rec = patient_obj.search([('state', '=', 'done'),
                                       ('year', '=', self.academic_year_id.id)])
        for pat in done_rec:
            practice_seq = pat.practice_id.practice_id.sequence
            next_class_id = practice_obj.next_account(practice_seq)
            # Assign the academic year
            if next_class_id:
                type = pat.practice_id.type_id.id or False
                next_pract = podiatry_pract_obj.search([
                    ('practice_id', '=', next_class_id),
                    ('type_id', '=', type),
                    ('podiatry_id', '=', pat.podiatry_id.id)])
                if next_pract:
                    pract_vals = {'year': next_year_id.id,
                                  'practice_id': next_pract.id}
                    # Move patient to next practice
                    pat.write(pract_vals)
