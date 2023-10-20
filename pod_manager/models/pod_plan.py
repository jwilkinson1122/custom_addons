# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PodPlanActivityType(models.Model):
    _name = 'pod.plan.activity.type'
    _description = 'Plan activity type'
    _rec_name = 'summary'


    activity_type_id = fields.Many2one(
        'mail.activity.type', 'Activity Type',
        default=lambda self: self.env.ref('mail.mail_activity_data_todo'),
        domain=lambda self: ['|', ('res_model', '=', False), ('res_model', '=', 'pod.practitioner')],
        ondelete='restrict'
    )
    summary = fields.Char('Summary', compute="_compute_default_summary", store=True, readonly=False)
    responsible = fields.Selection([
        ('assistant', 'Assistant'),
        ('manager', 'Manager'),
        ('practitioner', 'Practitioner'),
        ('other', 'Other')], default='practitioner', string='Responsible', required=True)
    # sgv todo change back to 'Responsible Person'
    responsible_id = fields.Many2one('res.users', 'Name', help='Specific responsible of activity if not linked to the practitioner.')
    note = fields.Html('Note')


    @api.depends('activity_type_id')
    def _compute_default_summary(self):
        for plan_type in self:
            if not plan_type.summary and plan_type.activity_type_id and plan_type.activity_type_id.summary:
                plan_type.summary = plan_type.activity_type_id.summary

    def get_responsible_id(self, practitioner):
        if self.responsible == 'assistant':
            if not practitioner.assistant_id:
                raise UserError(_('Assistant of practitioner %s is not set.', practitioner.name))
            responsible = practitioner.assistant_id.user_id
            if not responsible:
                raise UserError(_('User of assistant of practitioner %s is not set.', practitioner.name))
        elif self.responsible == 'manager':
            if not practitioner.parent_id:
                raise UserError(_('Manager of practitioner %s is not set.', practitioner.name))
            responsible = practitioner.parent_id.user_id
            if not responsible:
                raise UserError(_('User of manager of practitioner %s is not set.', practitioner.name))
        elif self.responsible == 'practitioner':
            responsible = practitioner.user_id
            if not responsible:
                raise UserError(_('User linked to practitioner %s is required.', practitioner.name))
        elif self.responsible == 'other':
            responsible = self.responsible_id
            if not responsible:
                raise UserError(_('No specific user given on activity %s.', self.activity_type_id.name))
        return responsible


class PodPlan(models.Model):
    _name = 'pod.plan'
    _description = 'plan'

    name = fields.Char('Name', required=True)
    plan_activity_type_ids = fields.Many2many('pod.plan.activity.type', string='Activities')
    active = fields.Boolean(default=True)
