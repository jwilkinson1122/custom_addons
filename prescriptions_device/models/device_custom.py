# -*- coding: utf-8 -*-


from odoo import fields, models


class DeviceCustom(models.Model):
    _name = 'device.custom'
    _inherit = ['device.custom', 'prescriptions.mixin']

    prescriptions_device_settings = fields.Boolean(related="company_id.prescriptions_device_settings", string="Centralize Device Prescriptions")
    prescription_count = fields.Integer(compute='_compute_prescription_count', string='Prescriptions')

    def _compute_prescription_count(self):
        prescription_data = self.env['prescriptions.prescription']._read_group([
            ('res_id', 'in', self.ids), ('res_model', '=', self._name)],
            groupby=['res_id'], aggregates=['__count'])
        mapped_data = dict(prescription_data)
        for record in self:
            record.prescription_count = mapped_data.get(record.id, 0)

    def _get_prescription_folder(self):
        return self.company_id.prescriptions_device_folder

    def _get_prescription_owner(self):
        return self.env.user

    def _get_prescription_tags(self):
        return self.company_id.prescriptions_device_tags

    def _check_create_prescriptions(self):
        return self.company_id.prescriptions_device_settings and super()._check_create_prescriptions()

    def action_open_attachments(self):
        self.ensure_one()
        if not self.company_id.prescriptions_device_settings:
            return True
        device_folder = self._get_prescription_folder()
        device_tags = self._get_prescription_tags()
        action = self.env['ir.actions.act_window']._for_xml_id('prescriptions.prescription_action')
        action['domain'] = [('res_model', '=', self._name), ('res_id', '=', self.id),]
        action['context'] = {
            'default_res_id': self.id,
            'default_res_model': self._name,
            'searchpanel_default_folder_id': device_folder.id,
            'searchpanel_default_tag_ids': device_tags.ids,
        }
        return action
