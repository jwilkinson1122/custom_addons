# See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class MoveStandards(models.TransientModel):
    """Defining TransientModel to move standard."""

    _name = "move.standards"
    _description = "Move Standards"

    academic_year_id = fields.Many2one(
        "academic.year",
        "Academic Year",
        required=True,
        help="""
The Acedemic year from which you need to move the patient to next Year.""",
    )

    def move_start(self):
        """Code for moving patient to next standard"""
        academic_obj = self.env["academic.year"]
        podiatry_stand_obj = self.env["podiatry.standard"]
        standard_obj = self.env["standard.standard"]
        patient_obj = self.env["patient.patient"]
        next_year_id = academic_obj.next_year(self.academic_year_id.sequence)
        if not next_year_id:
            raise ValidationError(
                _(
                    "The next sequanced Acedemic year after the selected "
                    "one is not configured!"
                )
            )
        done_rec = patient_obj.search(
            [("state", "=", "done"), ("year", "=", self.academic_year_id.id)]
        )
        for patient in done_rec:
            standard_seq = patient.standard_id.standard_id.sequence
            next_class_id = standard_obj.next_standard(standard_seq)
            # Assign the academic year
            if next_class_id:
                division = patient.standard_id.division_id.id or False
                next_stand = podiatry_stand_obj.search(
                    [
                        ("standard_id", "=", next_class_id),
                        ("division_id", "=", division),
                        ("practice_id", "=", patient.practice_id.id),
                        ("medium_id", "=", patient.medium_id.id),
                    ]
                )
                if next_stand:
                    std_vals = {
                        "year": next_year_id.id,
                        "standard_id": next_stand.id,
                    }
                    # Move patient to next standard
                    patient.write(std_vals)
