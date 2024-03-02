# -*- coding: utf-8 -*-


from odoo import fields, models


class PrescriptionServiceType(models.Model):
    _name = 'prescription.service.type'
    _description = 'Prescription Adjustment Type'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    category = fields.Selection([
        ('prescription', 'Prescription'),
        ('service', 'Adjustment')
        ], 'Category', required=True, help='Choose whether the service refer to prescription, prescription services or both')
