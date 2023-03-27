from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'




    patient_id = fields.Many2one('hospital.patient', string="Patient")

    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string="Appointment", related='patient_id.appointment_ids')

    



