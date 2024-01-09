from odoo import models, fields, api, _


class User(models.Model):
    _inherit = 'res.users'

    is_treatment_professional = fields.Boolean(
        compute="_compute_is_treatment_professional", store=True)

    @api.depends('groups_id')
    def _compute_is_treatment_professional(self):
        for rec in self:
            rec.is_treatment_professional = rec.has_group(
                'pod_prescriptions_partner.group_prescriptions_partner_treatment_professional')
