# Copyright 2015 LasLabs
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models


class MedicalPrescriptionOrderLine(models.Model):
    _name = 'medical.prescription.order.line'
    _inherit = ['medical.prescription.order.line', 'mail.thread']
