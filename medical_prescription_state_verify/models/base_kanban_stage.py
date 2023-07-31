# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class BaseKanbanStage(models.Model):
    _inherit = 'base.kanban.stage'

    is_verified = fields.Boolean(
        string='Verified?',
    )
