# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class MedicalPrescriptionOrder(models.Model):
    _inherit = 'medical.prescription.order'

    def write(self, vals):
        """
        1) Limit changes to verified orders
        2) Move order lines to a hold state when their orders are verified
        3) Move order lines to an exception state when their orders are
        cancelled or marked as exceptions
        """
        STATE_MODULE = 'medical_prescription_state'
        cancelled_state = self.env.ref(
            STATE_MODULE + '.prescription_order_state_cancelled'
        )
        exception_state = self.env.ref(
            STATE_MODULE + '.prescription_order_state_exception'
        )
        post_verify_states = cancelled_state + exception_state

        verified_recs = self.filtered(lambda r: r.stage_id.is_verified)
        if verified_recs:
            for key in vals:
                if key != 'stage_id':
                    raise ValidationError(
                        _('You are trying to edit one or more prescriptions'
                          ' that have already been verified (e.g. %s). Please'
                          ' either cancel them or mark them as exceptions if'
                          ' manual changes are required.')
                        % verified_recs[0].name
                    )

                stage_model = self.env['base.kanban.stage']
                stage = stage_model.search([('id', '=', vals['stage_id'])])
                if stage not in post_verify_states:
                    raise ValidationError(
                        _('You are trying to move one or more verified'
                          ' prescriptions into a disallowed state (e.g. %s).'
                          ' Verified prescriptions can only be cancelled or'
                          ' marked as exceptions.') % verified_recs[0].name
                    )

        super_result = super(MedicalPrescriptionOrder, self).write(vals)

        verified_recs_now = self.filtered(lambda r: r.stage_id.is_verified)
        new_verified_recs = verified_recs_now - verified_recs
        line_hold_state = self.env.ref(
            STATE_MODULE + '.prescription_order_line_state_hold'
        )
        new_verified_recs.prescription_order_line_ids.write({
            'stage_id': line_hold_state.id,
        })

        canned_recs = self.filtered(lambda r: r.stage_id in post_verify_states)
        line_exception_state = self.env.ref(
            STATE_MODULE + '.prescription_order_line_state_exception'
        )
        canned_recs.prescription_order_line_ids.write({
            'stage_id': line_exception_state.id,
        })

        return super_result
