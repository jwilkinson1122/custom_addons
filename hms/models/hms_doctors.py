from odoo import fields,api,models
from odoo.exceptions import UserError


class Doctors(models.Model):
    _name="hms_doctors"
    first_name=fields.Char()
    last_name=fields.Char()
    image=fields.Binary()

    # relation
