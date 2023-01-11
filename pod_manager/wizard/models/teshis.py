# -*- coding: utf8 -*-

from odoo import models, fields, api


class TeshisWizard(models.TransientModel):
    _name = "podiatry.teshis.wizard"
    _description = "Teşhis Wizard"

    teshis_ids = fields.Many2many(
        'podiatry.ereport.teshis', string="Diagnostic List")
