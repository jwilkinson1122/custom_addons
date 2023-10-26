# -*- coding: utf-8 -*-


from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    prescription_minimum_threshold = fields.Float()
