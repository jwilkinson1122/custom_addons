# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CreatePrescriptionObj(models.TransientModel):
    _name = 'create.prescription.obj'
    _description = 'Create Prescription Line Item'

    practitioner_id = fields.Many2one(
        'podiatry.practitioner', string="Practitioner", required=True)

    product_id = fields.Many2one('product.product', 'Name')

    def create_prescription_obj(self):
        vals = {
            'practitioner_id': self.practitioner_id.id,
            'product_id': self.product_id.id,
            # 'name': self.name,
        }
        self.practitioner_id.message_post(
            body="Your New Prescription Has Been Added", subject="New Prescription Object")
        new_prescription_obj = self.env['podiatry.prescription.line'].create(
            vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'podiatry.prescription.line',
                'res_id': new_prescription_obj.id,
                'context': context
                }

    state = fields.Selection(
        selection="_selection_state", default="start", required=True
    )

    allow_back = fields.Boolean(compute="_compute_allow_back")

    @api.depends("state")
    def _compute_allow_back(self):
        for record in self:
            record.allow_back = getattr(
                record, "state_previous_%s" % record.state, False
            )

    @api.model
    def _selection_state(self):
        return [
            ('start', 'Start'),
            ('configure', 'Configure'),
            ('custom', 'Customize'),
            ('final', 'Final'),
        ]

    def open_next(self):
        state_method = getattr(self, "state_exit_{}".format(self.state), None)
        if state_method is None:
            raise NotImplementedError(
                "No method defined for state {}".format(self.state)
            )
        state_method()
        return self._reopen_self()

    def open_previous(self):
        state_method = getattr(
            self, "state_previous_{}".format(self.state), None)
        if state_method is None:
            raise NotImplementedError(
                "No method defined for state {}".format(self.state)
            )
        state_method()
        return self._reopen_self()

    def _reopen_self(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def _default_prescription_id(self):
        return self.env.context.get('active_id')

    def state_exit_start(self):
        self.state = 'configure'

    def state_exit_configure(self):
        self.state = 'custom'

    def state_exit_custom(self):
        self.state = 'final'

    def state_previous_configure(self):
        self.state = 'start'

    def state_previous_custom(self):
        self.state = 'configure'

    def state_previous_final(self):
        self.state = 'custom'
