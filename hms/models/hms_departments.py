from odoo import fields,api,models
from odoo.exceptions import UserError


class deprtments(models.Model):
    _name="hms.departments"
    name=fields.Char()
    capacity=fields.Integer()
    is_opened=fields.Boolean()
    patients=fields.One2many("hospital.patient","departments_ids")