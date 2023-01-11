# -*- coding: utf8 -*-

from odoo import models, fields, api


class EtkinMaddeDVOWizard(models.TransientModel):
    _name = "hospital.etkin_maddedvo.wizard"
    _description = "Etkin MaddeDVO Wizard"

    etkin_madde_ids = fields.Many2many(
        'hospital.etkin_maddedvo', string="Active Item List")
