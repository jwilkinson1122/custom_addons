# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    lice_number = fields.Char(string='Licence Number')
