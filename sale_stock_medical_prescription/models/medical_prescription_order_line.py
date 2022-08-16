# Copyright 2016 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from openerp import api, fields, models


class MedicalPrescriptionOrderLine(models.Model):
    _inherit = 'medical.prescription.order.line'

    dispense_uom_id = fields.Many2one(
        string='Dispense UoM',
        comodel_name='uom.uom',
        help='Dispense Unit of Measure',
        required=True,
        default=lambda s: s._default_dispense_uom_id(),
    )

    @api.model
    def _default_dispense_uom_id(self):
        return self.env['uom.uom'].\
            browse(self.env['product.template']._get_default_uom_id())
