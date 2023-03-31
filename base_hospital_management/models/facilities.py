# -*- coding: utf-8 -*-

from odoo import models, fields


class RoomFacility(models.Model):
    _name = 'hospital.facilities'
    _description = 'Room Facilities'
    _rec_name = 'facilities'

    facilities = fields.Text(string="Facilities", required="True")


class WardFacility(models.Model):
    _name = 'ward.facilities'
    _description = 'Ward Facilities'
    _rec_name = 'facilities'

    facilities = fields.Text(string="Facilities", required="True")

