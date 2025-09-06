from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"

    sale_secondary_uom_id = fields.Many2one(
        "product.secondary.unit",
        string="Default secondary unit for sales",
        related="product_tmpl_id.sale_secondary_uom_id",
        store=True,            # store if you need domain/search speed
        readonly=False,        # allow writing here to actually update the template field
    )

    # sale_secondary_uom_id = fields.Many2one(
    #     comodel_name="product.secondary.unit",
    #     string="Default secondary unit for sales",
    #     help="In order to set a value, please first add at least one record"
    #     " in 'Secondary Unit of Measure'",
    #     domain="['|', ('product_id', '=', id),"
    #     "'&', ('product_tmpl_id', '=', product_tmpl_id),"
    #     "     ('product_id', '=', False)]",
    # )
