# -*- coding: utf-8 -*-

from odoo import models, fields


class OrgContacts(models.Model):
    """This class is used to deal with contacts"""

    _name = "org.contacts"
    _description = "Contacts"

    contact_id = fields.Many2one("res.partner", string="Contact")
