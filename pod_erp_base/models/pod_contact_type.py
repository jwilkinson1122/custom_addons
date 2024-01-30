# -*- coding: utf-8 -*-
from odoo import fields, models, _

class ContactType(models.Model):
    _name = 'contact.type'
    _description = 'Adds Contacts Types for Contacts'

    name = fields.Char("Contact Type")