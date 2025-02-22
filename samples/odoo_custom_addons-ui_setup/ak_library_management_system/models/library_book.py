#-*- coding: utf-8 -*-
from odoo import models, fields


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = "This is the books class for managing the books"

    name=fields.Char(string='Book Title')
    author=fields.Char(string='Author Name')
    isbn=fields.Char(string='ISBN Number')
    category_id=fields.Many2one('library.book.category',string='Book Category')
    publication_date=fields.Date(string='Date of Publication')
    description=fields.Text(string=' Book Summary')
    state=fields.Selection([('available','Available'),('borrowed','Borrowed')],string='Book Availability',tracking=True,default="available")
    #book_tags_ids = fields.Many2one('library.book.tag', string='Tags')
    tags_ids = fields.Many2many('library.book.tag',related='category_id.tags_ids',string='Tags')

    # Update the state to the borrowed
    def action_change_state(self):
        self.write({'state': 'borrowed'})

    # Update the state to the available
    def action_state_available(self):
        self.write({'state':'available'})
