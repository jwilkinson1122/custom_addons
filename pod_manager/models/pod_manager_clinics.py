from odoo import fields, api, models
from odoo.exceptions import UserError


class Clinic(models.Model):
    _name = "pod_manager.clinic"
    name = fields.Char()
    capacity = fields.Integer()
    is_opened = fields.Boolean()
    patients = fields.One2many("clinic.patient", "clinic_ids")
