from odoo import api, exceptions, fields, models


class BookoutLine(models.Model):
    _name = "practice.bookout.line"
    _description = "Bookout Request Line"

    bookout_id = fields.Many2one("practice.bookout", required=True)
    prescription_id = fields.Many2one("practice.prescription", required=True)
    note = fields.Char("Notes")
    prescription_cover = fields.Binary(related="prescription_id.image")
