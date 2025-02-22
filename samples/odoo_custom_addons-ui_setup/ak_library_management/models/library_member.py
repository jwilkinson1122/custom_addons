#-*- coding: utf-8 -*-
from odoo import models, fields


class LibraryMember(models.Model):
    """This class contain details of members
    like name, contact number and membership date.
    """

    _name = 'library.member'
    _description = "This is the member class for managing the members"

    name = fields.Char(string = 'Member Name')
    email = fields.Char(string = 'Email ID')
    phone = fields.Char(string = 'Contact Number')
    membership_date = fields.Date(string = 'Membership Start Date')
