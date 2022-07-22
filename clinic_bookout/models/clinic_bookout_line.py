from odoo import api, exceptions, fields, models


class BookoutLine(models.Model):
    _name = "clinic.bookout.line"
    _description = "Bookout Request Line"

    bookout_id = fields.Many2one("clinic.bookout", required=True)
    prescription_id = fields.Many2one("clinic.prescription", required=True)
    note = fields.Char("Notes")
    prescription_cover = fields.Binary(related="prescription_id.image")
