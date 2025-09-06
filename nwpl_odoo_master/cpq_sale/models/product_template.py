
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cpq_description_sale_tmpl = fields.Text(
        string="Configurable Sale Description Template"
    )

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        res = super()._onchange_product_id_warning()
        if self.product_id.cpq_ok and self.product_id.cpq_description_sale_tmpl:
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang)

            name = product.product_tmpl_id._cpq_render_inline_template(
                product.cpq_description_sale_tmpl,
                extras={
                    "record": product,
                    "tmpl": self,
                },
            )

            if name:
                self.name = name
        return res

    # sale_secondary_uom_id = fields.Many2one(
    #     "product.secondary.unit",
    #     string="Default secondary unit for sales",
    #     help="Choose a secondary unit attached to this template.",
    #     domain="[('product_tmpl_id', '=', id), ('product_id', '=', False)]",
    #     store=True,
    # )

    # @api.onchange("sale_secondary_uom_id")
    # def _onchange_sale_secondary_uom_id(self):
    #     if self.sale_secondary_uom_id and self.sale_secondary_uom_id.product_id:
    #         return {
    #             "warning": {
    #                 "title": _("Warning"),
    #                 "message": _(
    #                     "You selected a secondary UoM linked to a specific variant. "
    #                     "For template-wide secondary UoM, pick one linked to the template."
    #                 ),
    #             }
    #         }
            
