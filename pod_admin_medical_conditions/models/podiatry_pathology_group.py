
from odoo import fields, models


class PodiatryPathologyGroup(models.Model):
    _name = 'podiatry.pathology.group'
    _description = 'Podiatry Pathology Group'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
    )
    notes = fields.Text(
        string='Notes',
        translate=True
    )
    code = fields.Char(
        required=True,
        help='for example MDG6 code will contain the Millennium Development\
        Goals # 6 conditions : Tuberculosis, Malaria and HIV/AIDS'
    )
    description = fields.Text(
        string='Short Description', required=True, translate=True
    )
