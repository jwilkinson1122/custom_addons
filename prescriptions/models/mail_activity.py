# -*- coding: utf-8 -*-


from odoo import api, models, fields, _


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def _prepare_next_activity_values(self):
        vals = super()._prepare_next_activity_values()
        current_activity_type = self.activity_type_id
        next_activity_type = current_activity_type.triggered_next_type_id

        if current_activity_type.category == 'upload_file' and self.res_model == 'prescriptions.prescription' and next_activity_type.category == 'upload_file':
            existing_prescription = self.env['prescriptions.prescription'].search([('request_activity_id', '=', self.id)], limit=1)
            if 'summary' not in vals:
                vals['summary'] = self.summary or _('Upload file request')
            new_doc_request = self.env['prescriptions.prescription'].create({
                'owner_id': existing_prescription.owner_id.id,
                'folder_id': next_activity_type.folder_id.id if next_activity_type.folder_id else existing_prescription.folder_id.id,
                'tag_ids': [(6, 0, next_activity_type.tag_ids.ids)],
                'name': vals['summary'],
            })
            vals['res_id'] = new_doc_request.id
        return vals

    def _action_done(self, feedback=False, attachment_ids=None):
        if self and attachment_ids:
            prescriptions = self.env['prescriptions.prescription'].search([
                ('request_activity_id', 'in', self.ids),
                ('attachment_id', '=', False)
            ])
            if prescriptions:
                to_remove = self.env['prescriptions.prescription'].search([('attachment_id', '=', attachment_ids[0])])
                if to_remove:
                    to_remove.unlink()
                if not feedback:
                    feedback = _("Prescription Request: %s Uploaded by: %s", prescriptions[0].name, self.env.user.name)
                prescriptions.write({
                    'attachment_id': attachment_ids[0],
                    'request_activity_id': False
                })

        return super(MailActivity, self)._action_done(feedback=feedback, attachment_ids=attachment_ids)

    @api.model_create_multi
    def create(self, vals_list):
        activities = super().create(vals_list)
        upload_activities = activities.filtered(lambda act: act.activity_category == 'upload_file')

        # link back prescriptions and activities
        upload_prescriptions_activities = upload_activities.filtered(lambda act: act.res_model == 'prescriptions.prescription')
        if upload_prescriptions_activities:
            prescriptions = self.env['prescriptions.prescription'].browse(upload_prescriptions_activities.mapped('res_id'))
            for prescription, activity in zip(prescriptions, upload_prescriptions_activities):
                if not prescription.request_activity_id:
                    prescription.request_activity_id = activity.id

        # create underlying prescriptions if related record is not a prescription
        doc_vals = [{
            'res_model': activity.res_model,
            'res_id': activity.res_id,
            'owner_id': activity.activity_type_id.default_user_id.id,
            'folder_id': activity.activity_type_id.folder_id.id,
            'tag_ids': [(6, 0, activity.activity_type_id.tag_ids.ids)],
            'name': activity.summary or activity.res_name or 'upload file request',
            'request_activity_id': activity.id,
        } for activity in upload_activities.filtered(
            lambda act: act.res_model != 'prescriptions.prescription' and act.activity_type_id.folder_id
        )]
        if doc_vals:
            self.env['prescriptions.prescription'].sudo().create(doc_vals)
        return activities
