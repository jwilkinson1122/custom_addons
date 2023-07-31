# -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalInsurancePlan(models.Model):
    _inherit = 'medical.insurance.plan'
    active = fields.Boolean(
        default=True
    )
    pricelist_id = fields.Many2one(
        string='Pricelist',
        comodel_name='product.pricelist',
        related='insurance_template_id.pricelist_id',
        readonly=True,
    )

    @api.model
    def create(self, vals):
        res = super(MedicalInsurancePlan, self).create(vals)
        res._save_pricelist_and_invalidate_plans()
        return res

    def write(self, vals):
        res = super(MedicalInsurancePlan, self).write(vals)
        if vals.get('active', True):
            self._save_pricelist_and_invalidate_plans()
        return res

    def _save_pricelist_and_invalidate_plans(self):
        for rec_id in self:
            if rec_id.patient_id:
                rec_id.patient_id.write({
                    'property_product_pricelist': rec_id.pricelist_id.id
                })
                plan_ids = rec_id.env['medical.insurance.plan'].search([
                    ['patient_id', '=', rec_id.patient_id.id],
                    ['id', '!=', rec_id.id],
                ])
                plan_ids.action_invalidate()

    def action_invalidate(self):
        self.write({'active': False})
