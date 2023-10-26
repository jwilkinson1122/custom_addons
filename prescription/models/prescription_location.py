# -*- coding: utf-8 -*-


from odoo import fields, models


class PrescriptionLocation(models.Model):
    _name = 'prescription.location'
    _description = 'Prescription Locations'

    name = fields.Char('Location Name', required=True)
    address = fields.Text('Address')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
