# -*- coding: utf-8 -*-


import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class PracticeProductProduct(models.Model):
    _name = "practice.product.product"
    _inherit = "product.product"
    _description = 'Podiatry Product model'

#    test_type = fields.Char(
#        required=True,
#        index=True
#    )
