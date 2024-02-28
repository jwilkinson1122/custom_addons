# -*- coding: utf-8 -*-

import json
from collections import defaultdict

from odoo import api, fields, models, _, _lt
from odoo.exceptions import UserError
from odoo.tools import frozendict


class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'prescriptions.mixin']

    use_prescriptions = fields.Boolean("Use Prescriptions", default=True)
    prescriptions_folder_id = fields.Many2one('prescriptions.folder', string="Workspace", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", copy=False,
        help="Workspace in which all of the prescriptions of this project will be categorized. All of the attachments of your tasks will be automatically added as prescriptions in this workspace as well.")
    prescriptions_tag_ids = fields.Many2many('prescriptions.tag', 'project_prescriptions_tag_rel', string="Default Tags", domain="[('folder_id', 'parent_of', prescriptions_folder_id)]", copy=True)
    prescription_count = fields.Integer(compute='_compute_attached_prescription_count', string="Number of prescriptions in Project", groups='prescriptions.group_prescriptions_user')
    shared_prescription_ids = fields.One2many('prescriptions.prescription', string='Shared Prescriptions', compute='_compute_shared_prescription_ids')
    shared_prescription_count = fields.Integer("Shared Prescriptions Count", compute='_compute_shared_prescription_ids')

    @api.constrains('prescriptions_folder_id')
    def _check_company_is_folder_company(self):
        for project in self:
            if project.prescriptions_folder_id and project.prescriptions_folder_id.company_id and project.company_id != project.prescriptions_folder_id.company_id:
                raise UserError(_('The "%s" workspace should either be in the "%s" company like this project or be open to all companies.', project.prescriptions_folder_id.name, project.company_id.name))

    def _compute_attached_prescription_count(self):
        Task = self.env['project.task']
        task_read_group = Task._read_group(
            [('project_id', 'in', self.ids)],
            ['project_id'],
            ['id:array_agg'],
        )
        task_ids = []
        task_ids_per_project_id = {}
        for project, ids in task_read_group:
            task_ids += ids
            task_ids_per_project_id[project.id] = ids
        Prescription = self.env['prescriptions.prescription']
        project_prescription_read_group = Prescription._read_group(
            [('res_model', '=', 'project.project'), ('res_id', 'in', self.ids)],
            ['res_id'],
            ['__count'],
        )
        prescription_count_per_project_id = dict(project_prescription_read_group)
        prescription_count_per_task_id = Task.browse(task_ids)._get_task_prescription_data()
        for project in self:
            task_ids = task_ids_per_project_id.get(project.id, [])
            project.prescription_count = prescription_count_per_project_id.get(project.id, 0) \
                + sum(
                    prescription_count_per_task_id.get(task_id, 0)
                    for task_id in task_ids
                )

    def _compute_shared_prescription_ids(self):
        tasks_read_group = self.env['project.task']._read_group(
            [('project_id', 'in', self.ids)],
            ['project_id'],
            ['id:array_agg'],
        )

        project_id_per_task_id = {}
        task_ids = []

        for project, ids in tasks_read_group:
            task_ids += ids
            for task_id in ids:
                project_id_per_task_id[task_id] = project.id

        prescriptions_read_group = self.env['prescriptions.prescription']._read_group(
            [
                '&',
                    ('is_shared', '=', True),
                    '|',
                        '&',
                            ('res_model', '=', 'project.project'),
                            ('res_id', 'in', self.ids),
                        '&',
                            ('res_model', '=', 'project.task'),
                            ('res_id', 'in', task_ids),
            ],
            ['res_model', 'res_id'],
            ['id:array_agg'],
        )

        prescription_ids_per_project_id = defaultdict(list)
        for res_model, res_id, ids in prescriptions_read_group:
            if res_model == 'project.project':
                prescription_ids_per_project_id[res_id] += ids
            else:
                project_id = project_id_per_task_id[res_id]
                prescription_ids_per_project_id[project_id] += ids

        for project in self:
            shared_prescription_ids = self.env['prescriptions.prescription'] \
                .browse(prescription_ids_per_project_id[project.id])
            project.shared_prescription_ids = shared_prescription_ids
            project.shared_prescription_count = len(shared_prescription_ids)

    @api.onchange('prescriptions_folder_id')
    def _onchange_prescriptions_folder_id(self):
        self.env['prescriptions.prescription'].search([
            ('res_model', '=', 'project.task'),
            ('res_id', 'in', self.task_ids.ids),
            ('folder_id', '=', self._origin.prescriptions_folder_id.id),
        ]).folder_id = self.prescriptions_folder_id
        self.prescriptions_tag_ids = False

    def _create_missing_folders(self):
        folders_to_create_vals = []
        projects_with_folder_to_create = []
        prescriptions_project_folder_id = self.env.ref('prescriptions_project.prescriptions_project_folder').id

        for project in self:
            if not project.prescriptions_folder_id:
                folder_vals = {
                    'name': project.name,
                    'parent_folder_id': prescriptions_project_folder_id,
                    'company_id': project.company_id.id,
                }
                folders_to_create_vals.append(folder_vals)
                projects_with_folder_to_create.append(project)

        created_folders = self.env['prescriptions.folder'].sudo().create(folders_to_create_vals)
        for project, folder in zip(projects_with_folder_to_create, created_folders):
            project.prescriptions_folder_id = folder

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        if not self.env.context.get('no_create_folder'):
            projects.filtered(lambda project: project.use_prescriptions)._create_missing_folders()
        return projects

    def write(self, vals):
        if 'company_id' in vals:
            for project in self:
                if project.prescriptions_folder_id and project.prescriptions_folder_id.company_id and len(project.prescriptions_folder_id.project_ids) > 1:
                    other_projects = project.prescriptions_folder_id.project_ids - self
                    if other_projects and other_projects.company_id.id != vals['company_id']:
                        lines = [f"- {project.name}" for project in other_projects]
                        raise UserError(_(
                            'You cannot change the company of this project, because its workspace is linked to the other following projects that are still in the "%s" company:\n%s\n\n'
                            'Please update the company of all projects so that they remain in the same company as their workspace, or leave the company of the "%s" workspace blank.',
                            other_projects.company_id.name, '\n'.join(lines), project.prescriptions_folder_id.name))

        if 'name' in vals and len(self.prescriptions_folder_id.project_ids) == 1 and self.name == self.prescriptions_folder_id.name:
            self.prescriptions_folder_id.name = vals['name']
        res = super().write(vals)
        if 'company_id' in vals:
            for project in self:
                if project.prescriptions_folder_id and project.prescriptions_folder_id.company_id:
                    project.prescriptions_folder_id.company_id = project.company_id
        if not self.env.context.get('no_create_folder'):
            self.filtered('use_prescriptions')._create_missing_folders()
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        # We have to add no_create_folder=True to the context, otherwise a folder
        # will be automatically created during the call to create.
        # However, we cannot use with_context, as it intanciates a new recordset,
        # and this copy would call itself infinitely.
        previous_context = self.env.context
        self.env.context = frozendict(self.env.context, no_create_folder=True)
        project = super().copy(default)
        self.env.context = previous_context

        if not self.env.context.get('no_create_folder') and project.use_prescriptions and self.prescriptions_folder_id:
            project.prescriptions_folder_id = self.prescriptions_folder_id.copy({'name': project.name})
        return project

    def _get_stat_buttons(self):
        buttons = super(ProjectProject, self)._get_stat_buttons()
        if self.use_prescriptions:
            buttons.append({
                'icon': 'file-text-o',
                'text': _lt('Prescriptions'),
                'number': self.prescription_count,
                'action_type': 'object',
                'action': 'action_view_prescriptions_project',
                'additional_context': json.dumps({
                    'active_id': self.id,
                }),
                'show': self.use_prescriptions,
                'sequence': 20,
            })
        return buttons

    def action_view_prescriptions_project(self):
        self.ensure_one()
        return {
            'res_model': 'prescriptions.prescription',
            'type': 'ir.actions.act_window',
            'name': _("%(project_name)s's Prescriptions", project_name=self.name),
            'domain': [
            '|',
                '&',
                ('res_model', '=', 'project.project'), ('res_id', '=', self.id),
                '&',
                ('res_model', '=', 'project.task'), ('res_id', 'in', self.task_ids.ids)
            ],
            'view_mode': 'kanban,tree,form',
            'context': {'default_res_model': 'project.project', 'default_res_id': self.id, 'limit_folders_to_project': True, 'default_tag_ids': self.prescriptions_tag_ids.ids},
        }

    def _get_prescription_tags(self):
        return self.prescriptions_tag_ids

    def _get_prescription_folder(self):
        return self.prescriptions_folder_id

    def _check_create_prescriptions(self):
        return self.use_prescriptions and super()._check_create_prescriptions()
