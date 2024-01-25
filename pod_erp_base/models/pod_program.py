# -*- coding: utf-8 -*-
from odoo import fields, models, _

class PodPrograms(models.Model):
    _name = 'pod.program'
    _description = 'Adds Pod Programs for Contacts'

    name = fields.Char("Program")