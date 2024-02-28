# -*- coding: utf-8 -*-

from markupsafe import Markup, escape
from odoo import Command, fields, models, _


class WorkflowActionRuleTask(models.Model):
    _inherit = ['prescriptions.workflow.rule']

    create_model = fields.Selection(selection_add=[('project.task', "Task")])

    def create_record(self, prescriptions=None):
        rv = super(WorkflowActionRuleTask, self).create_record(prescriptions=prescriptions)
        if self.create_model == 'project.task':
            project = prescriptions.folder_id._get_project_from_closest_ancestor() if len(prescriptions.folder_id) == 1 else self.env['project.project']
            new_obj = self.env[self.create_model].create({
                'name': " / ".join(prescriptions.mapped('name')) or _("New task from Prescriptions"),
                'user_ids': [Command.set(self.env.user.ids)],
                'partner_id': prescriptions.partner_id.id if len(prescriptions.partner_id) == 1 else False,
                'project_id': project.id,
            })
            task_action = {
                'type': 'ir.actions.act_window',
                'res_model': self.create_model,
                'res_id': new_obj.id,
                'name': _("new %s from %s", self.create_model, new_obj.name),
                'view_mode': 'form',
                'views': [(False, "form")],
                'context': self._context,
            }
            if len(prescriptions) == 1:
                prescription_msg = _('Task created from prescription %s', prescriptions._get_html_link())
            else:
                prescription_msg = escape(_('Task created from prescriptions'))
                prescription_msg += Markup("<ul>%s</ul>") % Markup().join(
                    Markup("<li>%s</li>") % prescription._get_html_link()
                    for prescription in prescriptions)

            for prescription in prescriptions:
                this_prescription = prescription
                if (prescription.res_model or prescription.res_id) and prescription.res_model != 'prescriptions.prescription'\
                    and not (project and prescription.res_model == 'project.project' and prescription.res_id == project.id):
                    this_prescription = prescription.copy()
                    attachment_id_copy = prescription.attachment_id.with_context(no_prescription=True).copy()
                    this_prescription.write({'attachment_id': attachment_id_copy.id})

                # the 'no_prescription' key in the context indicates that this ir_attachment has already a
                # prescriptions.prescription and a new prescription shouldn't be automatically generated.
                this_prescription.attachment_id.with_context(no_prescription=True).write({
                    'res_model': self.create_model,
                    'res_id': new_obj.id
                })
            new_obj.message_post(body=prescription_msg)
            return task_action
        return rv
