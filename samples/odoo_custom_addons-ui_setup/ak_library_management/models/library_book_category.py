#-*- coding: utf-8 -*-
from odoo import models, fields


class LibraryBookCategory(models.Model):
	"""This class contain detail about types of
	category for books. 
	"""

	_name = 'library.book.category'
	_description = "This is the books  category class for managing the books"

	name = fields.Char(string = 'Category')
