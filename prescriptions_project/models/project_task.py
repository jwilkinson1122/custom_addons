# -*- coding: utf-8 -*-


import ast

from odoo import fields, models, _
from odoo.osv import expression


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'prescriptions.mixin']

    project_use_prescriptions = fields.Boolean("Use Prescriptions", related='project_id.use_prescriptions')
    prescriptions_folder_id = fields.Many2one('prescriptions.folder', related='project_id.prescriptions_folder_id')
    prescription_ids = fields.One2many('prescriptions.prescription', 'res_id', string='Prescriptions', domain=[('res_model', '=', 'project.task')])
    shared_prescription_ids = fields.One2many('prescriptions.prescription', string='Shared Prescriptions', compute='_compute_shared_prescription_ids')
    prescription_count = fields.Integer(compute='_compute_attached_prescription_count', string="Number of prescriptions in Task", groups='prescriptions.group_prescriptions_user')
    shared_prescription_count = fields.Integer("Shared Prescriptions Count", compute='_compute_shared_prescription_ids')

    def _get_task_prescription_data(self):
        domain = [('res_model', '=', 'project.task'), ('res_id', 'in', self.ids)]
        return dict(self.env['prescriptions.prescription']._read_group(domain, ['res_id'], ['__count']))

    def _compute_attached_prescription_count(self):
        tasks_data = self._get_task_prescription_data()
        for task in self:
            task.prescription_count = tasks_data.get(task.id, 0)

    def _compute_shared_prescription_ids(self):
        prescriptions_read_group = self.env['prescriptions.prescription']._read_group(
            [
                '&',
                    ('is_shared', '=', True),
                    '&',
                        ('res_model', '=', 'project.task'),
                        ('res_id', 'in', self.ids),
            ],
            ['res_id'],
            ['id:array_agg', '__count'],
        )
        prescription_ids_and_count_per_task_id = {res_id: ids_count for res_id, *ids_count in prescriptions_read_group}
        for task in self:
            task.shared_prescription_ids, task.shared_prescription_count = prescription_ids_and_count_per_task_id.get(task.id, (False, 0))

    def unlink(self):
        # unlink prescriptions.prescription directly so mail.activity.mixin().unlink is called
        self.env['prescriptions.prescription'].sudo().search([('attachment_id', 'in', self.attachment_ids.ids)]).unlink()
        return super(ProjectTask, self).unlink()

    def _get_prescription_tags(self):
        return self.project_id.prescriptions_tag_ids

    def _get_prescription_folder(self):
        return self.project_id.prescriptions_folder_id

    def _check_create_prescriptions(self):
        return self.project_use_prescriptions and super()._check_create_prescriptions()

    def _get_attachments_search_domain(self):
        self.ensure_one()
        return expression.AND([
            super()._get_attachments_search_domain(),
            [('prescription_ids', '=', False)],
        ])

    def action_view_prescriptions_project_task(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('prescriptions_project.action_view_prescriptions_project_task')
        action['context'] = {
            **ast.literal_eval(action['context'].replace('active_id', str(self.id))),
            'default_tag_ids': self.project_id.prescriptions_tag_ids.ids,
        }
        return action

    def action_open_shared_prescriptions(self):
        self.ensure_one()
        return {
            'name': _("Task's Prescriptions"),
            'type': 'ir.actions.act_url',
            'url': f"/my/tasks/{self.id}/prescriptions/",
        }
