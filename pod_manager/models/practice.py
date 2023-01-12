# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class Practice(models.Model):

    _name = "podiatry.practice"
    _description = "Practice"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, tracking=True)
    active = fields.Boolean(string='Active', default='True', tracking=True)
    image = fields.Image(string="Image")
