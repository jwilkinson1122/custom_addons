
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cpq_description_sale_tmpl = fields.Text(
        string="Configurable Sale Description Template"
    )
