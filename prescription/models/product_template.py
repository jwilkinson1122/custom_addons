

from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # sale_ok = fields.Boolean(default=True, string="Can be Configured")
    
    # description_sale = fields.Text(
    #     'Prescription Description', translate=True,
    #     help="A description of the Product that you want to communicate to your customers. "
    #          "This description will be copied to every Prescription Order")


