from odoo.tests import TransactionCase


class TestPrescriptionOrderLineVariantDescription(TransactionCase):
    def setUp(self):
        super(TestPrescriptionOrderLineVariantDescription, self).setUp()
        self.fiscal_position_model = self.env["account.fiscal.position"]
        self.tax_model = self.env["account.tax"]
        self.pricelist_model = self.env["product.pricelist"]
        self.uom_uom_model = self.env["uom.uom"]
        self.product_tmpl_model = self.env["product.template"]
        self.product_model = self.env["product.product"]
        self.so_model = self.env["prescription.order"]
        self.so_line_model = self.env["prescription.order.line"]
        self.partner = self.env.ref("base.res_partner_1")

    def test_product_id_change(self):
        pricelist = self.pricelist_model.search([("name", "=", "Public Pricelist")])[0]
        uom = self.uom_uom_model.search([("name", "=", "Units")])[0]
        tax_include = self.tax_model.create(
            dict(name="Include tax", amount="0.21", price_include=True)
        )
        product_tmpl = self.product_tmpl_model.create(
            dict(
                name="Product template",
                list_price="121",
                taxes_id=[(6, 0, [tax_include.id])],
            )
        )
        product_tmpl.product_variant_id.update(
            dict(
                variant_description_prescription="Product variant description",
            )
        )
        product = product_tmpl.product_variant_id
        fp = self.fiscal_position_model.create(dict(name="fiscal position", sequence=1))
        rx = self.so_model.create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "fiscal_position_id": fp.id,
            }
        )
        rx_line = self.so_line_model.create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": 1.0,
                "product_uom": uom.id,
                "price_unit": 121.0,
                "order_id": rx.id,
            }
        )
        rx_line._onchange_product_id_warning()
        self.assertEqual(product.variant_description_prescription, rx_line.name)