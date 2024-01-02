# -*- coding: utf-8 -*-


from odoo import fields, models

class PrescriptionkWarnUncompleteMove(models.TransientModel):
    _name = 'prescription.warn.uncomplete.move'
    _description = 'Warn Uncomplete Move(s)'

    prescription_ids = fields.Many2many('prescription.order', string='Prescription Orders')

    def action_validate(self):
        self.ensure_one()
        return self.prescription_ids.action_prescription_done()
