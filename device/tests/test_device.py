from odoo.tests.common import TransactionCase


# @tagged('-at_install', 'post_install')
class TestDeviceState(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestDeviceState, self).setUp(*args, **kwargs)
        self.test_category = self.env["device.category"].create(
            {"name": "specie 1"})
        self.test_type = self.env["device.type"].create(
            {"name": "type 1", "category_id": self.test_category.id}
        )
        self.test_device = self.env["device"].create(
            {
                "name": "Device 1",
                "category_id": self.test_category.id,
                "type_id": self.test_type.id,
            }
        )

    def test_onchange_category(self):
        self.test_device.onchange_category()
        self.assertEqual(
            self.test_device.type_id.id,
            False,
            "Device type_id should be changed to False",
        )

    def test_onchange_type(self):
        self.test_device.onchange_type()
        self.assertEqual(
            self.test_device.color_id.id,
            False,
            "Device color_id should be changed to False",
        )
