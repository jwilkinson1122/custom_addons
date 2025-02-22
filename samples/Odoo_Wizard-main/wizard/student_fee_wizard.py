from odoo import fields, models


class StudentFeeWizard(models.TransientModel):
    _name = 'student.fee.wizard'

    total_fees = fields.Float(string='Total fees')

    def student_fee_update(self):
        print("yeah success full click on update")
        self.env['student.profile'].browse(self._context.get('active_ids')).update({'total_fees': self.total_fees})
        return True
