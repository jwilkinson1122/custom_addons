from odoo import models, fields

class DuckModel(models.Model):
    _name = 'duck.model'
    _description = 'Duck Store Model'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    color = fields.Char(string="Color")
    gender = fields.Selection([
       ('other', 'Other'),
       ('male', 'Male'),
       ('female', 'Female'),
    ], srting='Gender', default='other')
    