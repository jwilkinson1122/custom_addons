# -*- coding: utf-8 -*-

from odoo import models, fields


class NoteMaker(models.Model):
    """This class is used to deal with notes"""

    _name = "note.maker"
    _description = "note maker"

    note = fields.Text(string="Note", help="Tex field for note")
    user_id = fields.Many2one("res.users", string="User")
    note_title = fields.Char(string="Title", help="Title for the note")
