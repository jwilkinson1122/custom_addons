
from odoo import fields, models


class PodiatryPatient(models.Model):
    _inherit = 'podiatry.patient'

    def action_invalidate(self):
        super(PodiatryPatient, self).action_invalidate()
        self.condition_ids.action_invalidate()

    def compute_count_condition_ids(self):
        self.count_condition_ids = len(self.condition_ids)

    condition_ids = fields.One2many(
        comodel_name='podiatry.patient.condition',
        inverse_name='patient_id',
        string='Conditions'
    )
    count_condition_ids = fields.Integer(
        compute='compute_count_condition_ids',
        string='NB. Condition'
    )
