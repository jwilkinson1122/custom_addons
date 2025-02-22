#-*- coding: utf-8 -*-
from odoo import models, fields


class LibraryBookTag(models.Model):
    _name = 'library.book.tag'
    _description = "This is provide tags for the books."

    name=fields.Char(string='Book Tags')
