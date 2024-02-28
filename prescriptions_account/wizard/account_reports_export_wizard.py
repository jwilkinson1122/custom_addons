# -*- coding: utf-8 -*-


from odoo import api, models, fields, _


class ReportExportWizard(models.TransientModel):
    """ Extends the report export wizard to give it the ability to save the
    attachments it generates as prescriptions, in a folder of the Prescriptions app.
    """
    _inherit = 'account_reports.export.wizard'

    def _get_default_folder(self):
        company = self.env.company
        return company.account_folder if company.prescriptions_account_settings else self.env.ref('prescriptions.prescriptions_finance_folder', raise_if_not_found=False)

    folder_id = fields.Many2one(string="Folder", comodel_name='prescriptions.folder',
        help="Folder where to save the generated file", required=True,
        default=_get_default_folder)
    tag_ids = fields.Many2many('prescriptions.tag', 'export_wiz_prescription_tag_rel', string="Tags", domain="[('folder_id', '=', folder_id)]")

    @api.onchange('folder_id')
    def on_folder_id_change(self):
        self.tag_ids = False

    def export_report(self):
        # When making the export with Prescriptions app installed, we want the resulting action to open the folder of Prescriptions where
        # the attachments were saved, with only them visible, instead of the regular ir.attachment objects.
        self.ensure_one()
        created_attachments = self.env['prescriptions.prescription']
        for vals in self._get_attachments_to_save():
            created_attachments |= self.env['prescriptions.prescription'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Prescriptions'),
            'view_mode': 'kanban',
            'res_model': 'prescriptions.prescription',
            'domain': [],
            'context': {'searchpanel_default_folder_id': self.folder_id.id, 'searchpanel_default_tag_ids': self.tag_ids.ids},
            'view_id': self.env.ref('prescriptions.prescription_view_kanban').id,
        }


class ReportExportWizardOption(models.TransientModel):
    _inherit = 'account_reports.export.wizard.format'

    def get_attachment_vals(self, file_name, file_content, mimetype, log_options_dict):
        rslt = super(ReportExportWizardOption, self).get_attachment_vals(file_name, file_content, mimetype, log_options_dict)
        # Setting the folder_id of the attachment will make it appear in Prescriptions
        rslt['folder_id'] = self.export_wizard_id.folder_id.id
        rslt['tag_ids'] = [(6, 0, self.export_wizard_id.tag_ids.ids)]
        return rslt
