# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalPrescriptionOrderLine(models.Model):
    _inherit = 'medical.prescription.order.line'
    active = fields.Boolean(
        store=True,
        index=True,
        compute='_compute_active',
    )
    is_treatment_stopped = fields.Boolean(
        store=True,
        compute='_compute_is_treatment_stopped'
    )

    @api.depends('is_course_complete', 'is_treatment_stopped')
    def _compute_active(self, ):
        for rec_id in self:
            if rec_id.is_course_complete or rec_id.is_treatment_stopped:
                rec_id.active = False
            else:
                rec_id.active = True

    @api.depends('date_stop_treatment')
    def _compute_is_treatment_stopped(self, ):
        for rec_id in self:
            if not rec_id.date_stop_treatment:
                rec_id.is_treatment_stopped = False
            else:
                stop_date = fields.Datetime.from_string(
                    rec_id.date_stop_treatment
                )
                today = fields.Datetime.from_string(fields.Datetime.now())
                days = (today - stop_date).days
                rec_id.is_treatment_stopped = (days > 0)
