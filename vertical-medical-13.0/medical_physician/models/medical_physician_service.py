# -*- coding: utf-8 -*-
# Copyright 2008 Luis Falcon <lfalcon@gnusolidario.org>
# © 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalPhysicianService(models.Model):
    """
    Services provided by the Physician on a specific medical center.

    A physician could have "surgeries" on one center but only
    "general consultation" in another center,
    or the same service with different prices for each medical center.
    That's the reason to link this to res.partner instead of
    medical_physician.
    """
    _name = 'medical.physician.service'
    _inherits = {'product.product': 'product_id', }
    _description = 'Medical Physicians Services'

    product_id = fields.Many2one(
        string='Related Product',
        help='Product related information for Appointment Type',
        comodel_name='product.product',
        required=True,
        ondelete='restrict',
    )
    physician_id = fields.Many2one(
        string='Physician',
        help='The physician for the appointment',
        comodel_name='medical.physician',
        required=True,
        index=True,
        ondelete='cascade',
    )
