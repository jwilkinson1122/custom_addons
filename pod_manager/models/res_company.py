# -*- coding: utf-8 -*-

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    pod_existence_control_email_amount = fields.Integer(string="# emails to send")
    pod_existence_control_ip_list = fields.Char(string="Valid IP addresses")
