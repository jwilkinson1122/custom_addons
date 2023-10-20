# -*- coding: utf-8 -*-

import threading
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    resource_calendar_id = fields.Many2one(
        'resource.calendar', 'Company Practiceing Hours',
        related='company_id.resource_calendar_id', readonly=False)
    module_pod_existence = fields.Boolean(string="Advanced Existence Control")
    module_pod_skills = fields.Boolean(string="Skills Management")
    pod_existence_control_login = fields.Boolean(string="Based on user status in system", config_parameter='pod_manager.pod_existence_control_login')
    pod_existence_control_email = fields.Boolean(string="Based on number of emails sent", config_parameter='pod_existence.pod_existence_control_email')
    pod_existence_control_ip = fields.Boolean(string="Based on IP Address", config_parameter='pod_existence.pod_existence_control_ip')
    module_pod_attendance = fields.Boolean(string="Based on attendances")
    pod_existence_control_email_amount = fields.Integer(related="company_id.pod_existence_control_email_amount", readonly=False)
    pod_existence_control_ip_list = fields.Char(related="company_id.pod_existence_control_ip_list", readonly=False)
    pod_practitioner_self_edit = fields.Boolean(string="Practitioner Editing", config_parameter='pod_manager.pod_practitioner_self_edit')

    @api.constrains('module_pod_existence', 'pod_existence_control_email', 'pod_existence_control_ip')
    def _check_advanced_existence(self):
        test_mode = self.env.registry.in_test_mode() or getattr(threading.current_thread(), 'testing', False)
        if self.env.context.get('install_mode', False) or test_mode:
            return

        for settings in self:
            if settings.module_pod_existence and not (settings.pod_existence_control_email or settings.pod_existence_control_ip):
                raise ValidationError(_('You should select at least one Advanced Existence Control option.'))
