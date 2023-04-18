from odoo import fields, models, api


class Doctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Description'
    name = fields.Char()
    specializes = fields.Many2many(
        comodel_name='hospital.specialize',
        relation="doctor_specializes",
        column1="doctor_id",
        column2="specialize_id",
        string='Specializes')
    
    age = fields.Integer(
        string='Age', 
        required=False)


class Specialize(models.Model):
    _name = 'hospital.specialize'
    _description = 'Description'

    name = fields.Char(
        string='Name',
        required=False)
