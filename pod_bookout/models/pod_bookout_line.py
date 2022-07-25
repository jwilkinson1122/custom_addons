from odoo import api, exceptions, fields, models


class BookoutLine(models.Model):
    _name = "pod.bookout.line"
    _description = "Bookout Request Line"

    bookout_id = fields.Many2one("pod.bookout", required=True)
    prescription_id = fields.Many2one("pod.prescription", required=True)
    note = fields.Char("Notes")
    prescription_cover = fields.Binary(related="prescription_id.image")
