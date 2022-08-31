from odoo import models, fields, api


class PodiatryMedicalTest(models.Model):
    _name = 'pod.podtest'
    _description = 'Medical Test'

    name = fields.Char(string="Medical test name", required=True)
    price = fields.Integer(string="Price", required=True)
    pod_test_ids = fields.Many2many(string="Medical tests")
