# -*- coding: utf-8 -*-

from odoo import fields, models


class PodPlanWizard(models.TransientModel):
    _name = 'pod.plan.wizard'
    _description = 'Plan Wizard'

    plan_id = fields.Many2one('pod.plan', default=lambda self: self.env['pod.plan'].search([], limit=1))
    practitioner_id = fields.Many2one(
        'pod.practitioner', string='Practitioner', required=True,
        default=lambda self: self.env.context.get('active_id', None),
    )

    def action_launch(self):
        for activity_type in self.plan_id.plan_activity_type_ids:
            responsible = activity_type.get_responsible_id(self.practitioner_id)

            if self.env['pod.practitioner'].with_user(responsible).check_access_rights('read', raise_exception=False):
                date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type.activity_type_id)
                self.practitioner_id.activity_schedule(
                    activity_type_id=activity_type.activity_type_id.id,
                    summary=activity_type.summary,
                    note=activity_type.note,
                    user_id=responsible.id,
                    date_deadline=date_deadline
                )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pod.practitioner',
            'res_id': self.practitioner_id.id,
            'name': self.practitioner_id.display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }
