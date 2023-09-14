

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    supplier_info_ids = fields.One2many(
        "product.supplierinfo", inverse_name="name", check_company=True
    )

    third_party_supplier_info_ids = fields.One2many(
        "product.supplierinfo",
        inverse_name="third_party_partner_id",
        check_company=True,
    )

    def action_view_product_supplierinfo(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "product.product_supplierinfo_type_action"
        )
        action["domain"] = [
            "|",
            ("name", "=", self.id),
            ("third_party_partner_id", "=", self.id),
        ]
        return action
