#-*- coding: utf-8 -*-
from odoo import models, fields


class LibraryBook(models.Model):
	"""This class basically contains Book related informations
	like name,authors and publication date.
	"""

	_name = 'library.book'
	_description = "This is the books class for managing the books"

	name = fields.Char(string = 'Book Title')
	author = fields.Char(string = 'Author Name')
	isbn = fields.Char(string = 'ISBN Number')
	category_id = fields.Many2one('library.book.category',string = 'Book Category')
	publication_date = fields.Date(string = 'Date of Publication')
	description = fields.Text(string = 'Book Summary')
	state = fields.Selection([('available','Available'),('borrowed','Borrowed')],string = 'Book 	Availability', tracking = True, default = "available")

   
	def action_change_state(self):
		"""This method for change
		state to borrowed
		"""
		self.write({'state': 'borrowed'})


	def action_state_available(self):
		"""This method for change
		state to available
		"""
		self.write({'state':'available'})
