from .common import CommonCase


class TestProductBrand(CommonCase):
    def test_products_count(self):
        self.assertEqual(
            self.nwpl_pod_master.products_count, 0, "Error product count does not match"
        )
        self.product.product_brand_id = self.product_brand.id
        self.assertEqual(
            self.nwpl_pod_master.products_count, 1, "Error product count does not match"
        )
