# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_rounding_procedure(models.Model):
    _name = 'podiatry.rounding_procedure'
    _description = 'podiatry rounding procedure'

    notes = fields.Text(string="Notes")
    podiatry_patient_rounding_procedure_id = fields.Many2one(
        'podiatry.patient.rounding', string="Vaccines")
