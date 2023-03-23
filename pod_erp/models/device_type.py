from odoo import api, fields, models,_

class DeviceType(models.Model):
    _name ='device.type'
    _rec_name = 'name'
    
    name = fields.Char(string='Device_type',required=True)
