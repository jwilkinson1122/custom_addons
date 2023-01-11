from odoo import models, fields


class ResUsersDoctor(models.Model):
    _inherit = 'res.users'

    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")
    image = fields.Image(related="doctor_id.image")
    name = fields.Char(related="doctor_id.name")
    surname = fields.Char(related="doctor_id.surname")
    birth = fields.Date(related="doctor_id.birth")
    age = fields.Integer(related="doctor_id.age")
    doctor_tc = fields.Char(related="doctor_id.doctor_tc")
    brans_kod = fields.Char(related="doctor_id.brans_kod")
    sertifika_kod = fields.Selection([
        ('0', 'Yok'),
        ('56', 'Hemodiyaliz'),
        ('109', 'Aile Hekimliği')
    ], string="Sertifika Kod", related="doctor_id.sertifika_kod")
    test = fields.Char(string="test")
