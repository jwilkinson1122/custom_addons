# Copyright 2015 LasLabs Dave Lasley <dave@laslabs.com>
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import fields, models


class MedicalMedicament(models.Model):
    _inherit = 'medical.medicament'

    color_id = fields.Many2one(
        comodel_name='medical.medicament.attribute.color',
        string='Color',
    )
    shape_id = fields.Many2one(
        comodel_name='medical.medicament.attribute.shape',
        string='Shape',
    )
    flavor_id = fields.Many2one(
        comodel_name='medical.medicament.attribute.flavor',
        string='Flavor',
    )
