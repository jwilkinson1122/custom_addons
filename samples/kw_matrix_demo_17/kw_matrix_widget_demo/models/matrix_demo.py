import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class WidgetDemo(models.Model):
    _name = 'kw.matrix.widget.demo'
    _description = 'Matrix widget demo'

    name = fields.Char()
    matrix_data = fields.Text()
