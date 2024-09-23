import logging
import base64
from random import randint
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import file_open

_logger = logging.getLogger(__name__)

class UomUom(models.Model):
    _inherit = 'uom.uom'

    symbol = fields.Char(help="Degree sign, to be used with corrections.", required=True)