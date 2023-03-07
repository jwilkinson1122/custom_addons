# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class hotel_grivia(models.Model):
#     _name = 'hotel_grivia.hotel_grivia'
#     _description = 'hotel_grivia.hotel_grivia'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
