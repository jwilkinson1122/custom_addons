# -*- coding: utf-8 -*-
from odoo import fields, models, _

class PodStatus(models.Model):
    _name = 'pod.status'
    _description = 'Adds Status for Contacts'

    name = fields.Char("Status")