from odoo import api, fields, models,_

class TestType(models.Model):
    _name ='foot.test.type'
    _rec_name = 'name'

    name = fields.Char(string='Test_type',required=True)









