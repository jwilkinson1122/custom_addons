from odoo import models, fields, api

class PracticeMedicalTest(models.Model):
    _name = 'pod_erp.medicaltest'
    _description = 'Medical Test'

    name = fields.Char(string="Medical test name", required=True)
    price = fields.Integer(string="Price", required=True)
    medical_test_ids = fields.Many2many(string="Medical tests")