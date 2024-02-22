from odoo import _, api, fields, models


class ProductCustomerInfo(models.Model):
    _inherit = "product.supplierinfo"
    _name = "product.customerinfo"
    _description = "Customer Pricelist"

    partner_id = fields.Many2one(string="Customer", help="Customer of this product")

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": _("Import Template for Customer Pricelists"),
                "template": "/pod_product_info_for_customer/static/xls/"
                "product_customerinfo.xls",
            }
        ]
