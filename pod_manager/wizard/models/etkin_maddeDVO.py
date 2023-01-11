# -*- coding: utf8 -*-

from odoo import models, fields, api


class EtkinMaddeDVOWizard(models.TransientModel):
    _name = "podiatry.etkin_maddedvo.wizard"
    _description = "Etkin MaddeDVO Wizard"

    etkin_madde_ids = fields.Many2many(
        'podiatry.etkin_maddedvo', string="Active Item List")
