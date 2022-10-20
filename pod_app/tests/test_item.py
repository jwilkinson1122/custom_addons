from odoo.tests.common import TransactionCase


class TestItem(TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)
        self.Item = self.env["pod.item"]
        self.item1 = self.Item.create({
            "name": "Odoo Development Essentials",
            "isbn": "879-1-78439-279-6"})

    def test_item_create(self):
        "New Items are active by default"
        self.assertEqual(
            self.item1.active, True
        )

    def test_check_isbn(self):
        "Check valid ISBN"
        self.assertTrue(self.item1._check_isbn)
