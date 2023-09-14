

from odoo.tests.common import TransactionCase


class TestConfigSettings(TransactionCase):
    def test_config(self):
        product = self.env["product.product"].create(
            {"name": "Third Party Product", "type": "service"}
        )
        config = self.env["res.config.settings"].create({})
        config.def_third_party_product = product
        config.execute()
        config = self.env["res.config.settings"].create({})
        self.assertEqual(config.def_third_party_product, product)
