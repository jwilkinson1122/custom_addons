from odoo import fields, models


class PrescriptionForm(models.Model):

    _name = "prescription.form"
    _description = "Prescription Form"

    name = fields.Char()

    uom_ids = fields.Many2many("uom.uom")
