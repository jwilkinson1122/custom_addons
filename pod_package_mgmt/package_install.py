from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero
import subprocess
import sys

class PackageInstall(models.TransientModel):
    _name='package.install.wizard'
    name = fields.Char(string="Write Command")

    def action_install_now(self):
        command=self.name
        command=command.split(' ')
        result=subprocess.run([sys.executable, "-m", command[0], command[1], command[2]], capture_output=True,text=True)
        raise UserError(result.stdout)