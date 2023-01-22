# -*- coding: utf-8 -*-
from odoo import api, fields, models


class NewModule(models.TransientModel):
    _name = 'report.custom.template.console'

    parameters = fields.Text(string="Parameters")

    def button_action_apply(self):
        """
        {'section': 'section_other_options',
        'field': 'option_field_ids',
        'value': {'field_type': 'boolean', 'name_technical': 'show_logo', 'name': 'Show Logo ?', 'value_boolean': True},
        }
        """

        import ast

        report_id = self.env['report.custom.template'].browse(self._context['report_id'])
        params = ast.literal_eval(self.parameters)
        line_id = report_id.line_ids.filtered(lambda x: x.name_technical == params['section'])

        if not line_id:
            raise UserWarning('No Line: %s' % params['section'])

        # Other Options
        if params['field'] == 'option_field_ids':
            option = line_id.option_field_ids.filtered(lambda x: x.name_technical == params['value']['name_technical'])
            if option:
                option.unlink()
            line_id.option_field_ids = [(0, 0, params['value'])]
        else:
            raise UserWarning('No field: %s' % params['field'])

