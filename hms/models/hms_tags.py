from odoo import fields,api,models
from odoo.exceptions import UserError

class doctors_tags(models.Model):
    _name="hms.tags"

    name= fields.Char()