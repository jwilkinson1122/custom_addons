# -*- coding: utf-8 -*-
# Copyright 2008 Luis Falcon <lfalcon@gnusolidario.org>
# © 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalPhysicianScheduleTemplate(models.Model):
    """
    Available schedule for the Physician.

    ie: A physician will be able to say, in this schedule on this days.

    The objective is to show the available spaces for every physician
    """
    _name = 'medical.physician.schedule.template'
    _description = 'Medical Physicians Schedule Templates'

    physician_id = fields.Many2one(
        string='Physician',
        help='Physician for the schedule template',
        comodel_name='medical.physician',
        required=True,
        index=True,
        ondelete='cascade',
    )

