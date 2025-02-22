#-*- coding: utf-8 -*-
from odoo import models, fields


class LibraryBookCategory(models.Model):
    _name = 'library.book.category'
    _description = "This is the books  category class for managing the categories."

    name=fields.Char(string='Category')
    tags_ids=fields.Many2many('library.book.tag', string='Book Tag')


