# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalPrescriptionOrderLine(models.Model):
    _name = 'medical.prescription.order.line'
    _description = 'Medical Prescription Order Line'
    _inherit = ['medical.prescription.order.line', 'mail.thread']
