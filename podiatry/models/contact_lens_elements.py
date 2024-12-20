from odoo import models, api, fields


class ContactLensManufacturer(models.Model):
    _name = "contact.lens.manufacturer"

    name = fields.Char(required=True)
