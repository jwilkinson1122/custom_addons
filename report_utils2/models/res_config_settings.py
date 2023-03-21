# -*- coding: utf-8 -*-
import ast

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def open_custom_template(self):
        template_obj = self.env['report.custom.template']
        report_list = template_obj.get_report_list()
        report_name = self._context['report_name']
        company_id = False

        multi_company_applicable = report_list.get(report_name) and report_list.get(report_name).get('multi_company_applicable')
        if multi_company_applicable:
            company_id = self.company_id

        report_id = template_obj.get_template(report_name, company_id=company_id)

        if not report_id:
            if report_name not in report_list:
                raise UserError('We couldn\'t find report \'%s\'' % report_name)

            template_obj.reset_template(report_name, company_id=company_id)
            report_id = template_obj.get_template(report_name, company_id=company_id)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'report.custom.template',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': report_id.id,
        }
