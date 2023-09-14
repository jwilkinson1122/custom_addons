from odoo.tests.common import TransactionCase


class TestProductCommercial(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_obj = self.env["product.product"]
        self.product = self.product_obj.create(
            {
                "name": "Product",
                "commercial": "Commercial",
                "company_id": False,
                "default_code": "CODE",
            }
        )

    def test_name_search(self):
        search = self.product_obj.name_search("Product")
        aux = [a[0] for a in search]
        self.assertIn(self.product.id, aux)

    def test_name_search_commercial(self):
        aux = [a[0] for a in self.product_obj.name_search("Commercial")]
        self.assertIn(self.product.id, aux)

    def test_search(self):
        self.assertIn(
            self.product,
            self.product_obj.search([("name", "ilike", "Commercial")]),
        )

    def test_name(self):
        self.assertEqual(self.product.display_name, "[CODE] Product (Commercial)")
