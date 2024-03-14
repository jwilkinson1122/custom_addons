# -*- coding: utf-8 -*-
from odoo import models, fields, api



class ToothTooth(models.Model):
    _name = 'tooth.tooth'
    _description = 'Tooth'
    _order = 'sequence'
    name = fields.Char('Name')
    image = fields.Image("Image")
    sequence = fields.Integer("Sequence")

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'A name must be unique')
    ]