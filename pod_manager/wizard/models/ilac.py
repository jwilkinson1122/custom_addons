# -*- coding: utf8 -*-

from odoo import models, fields, api


class IlacWizard(models.TransientModel):
    _name = "podiatry.ilac.wizard"
    _description = "İlaç Wizard"

    ilac_listesi = fields.Many2many('podiatry.ilac', string="Product List")
