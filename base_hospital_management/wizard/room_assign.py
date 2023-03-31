""""Hospital Management"""
# -*- coding: utf-8 -*-

from odoo import fields, models


class RoomAssign(models.TransientModel):
    """Wizard for selecting the patient details in hospital"""
    _name = 'room.view'
    _description = 'room_assigning'

    patient_id = fields.Many2one('res.partner', 'Patient')
    responsible_person = fields.Many2one('res.partner', help="The person who take care of the patient")
    visting_time = fields.Float()
    room_no = fields.Many2one('patient.room')

    def patient_room_assigning(self):
        """updating the room for patients"""
        print(self.room_no,'rkjmkjm')
        val = self.env['hospital.inpatient'].search([('patient_id','=',self.patient_id.id)])
        val.write({
            'room_no' : self.room_no
        })
