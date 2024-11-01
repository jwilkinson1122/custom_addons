# -*- coding: utf-8 -*-
###################################################################################

# Author       :  A & M
# Copyright(c) :  2024-Present.
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

###################################################################################

import subprocess
from odoo import fields, models


class PipInstaller(models.Model):
    _name = "pip.installer"

    code_name = fields.Char(string='Python Script')
    code_method = fields.Selection([('install', 'Install'), ('upgrade', 'Upgrade'), ('uninstall', 'Uninstall'), ('show', 'Version')], string='Operation Type', default='install')

    def execute_pip(self):
        try:
            if self.code_method == 'uninstall':
                result = subprocess.run(['pip3', self.code_method, self.code_name, '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, input=b'y\n')
                html_text = result.stdout.decode('utf-8').replace("<", "&lt;").replace(">", "&gt;")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'sticky': True,
                        'message': html_text,
                    }
                }
            if self.code_method == 'upgrade':
                code_method = 'install'
                code_function = '--upgrade'
                result = subprocess.run(['pip3', code_method, code_function, self.code_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                html_text = result.stdout.decode('utf-8').replace("<", "&lt;").replace(">", "&gt;")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'sticky': True,
                        'message': html_text,
                    }
                }
            else:
                result = subprocess.run(['pip3', self.code_method, self.code_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                html_text = result.stdout.decode('utf-8').replace("<", "&lt;").replace(">", "&gt;")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'sticky': True,
                        'message': html_text,
                    }
                }
        except subprocess.CalledProcessError as error:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'sticky': True,
                    'message': error.stderr.decode('utf-8').replace("<", "&lt;").replace(">", "&gt;"),
                }
            }
