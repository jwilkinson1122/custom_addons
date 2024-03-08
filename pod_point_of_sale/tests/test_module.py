from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon
from odoo.addons.pod_point_of_sale.patch import (_get_modules_dict_auto_install_config)
# from ..models.base import disable_changeset

class TestModule(TransactionCase):
    _EXPECTED_RESULTS = {
        "web_responsive": {"web_responsive": True},
        "sale, purchase,": {"sale": True, "purchase": True},
        "web_responsive:web,base_technical_features:,"
        "point_of_sale:sale/purchase,account_usability": {
            "web_responsive": ["web"],
            "base_technical_features": [],
            "point_of_sale": ["sale", "purchase"],
            "account_usability": True,
        },
    }

    def test_config_parsing(self):
        for k, v in self._EXPECTED_RESULTS.items():
            self.assertEqual(_get_modules_dict_auto_install_config(k), v)


@tagged("post_install", "-at_install")
class TestUi(TestPointOfSaleHttpCommon):
    def test_pod_point_of_sale(self):
        self.main_pos_config.open_ui()

        before_orders = self.env["sale.order"].search(
            [("partner_id", "=", self.env.ref("base.res_partner_address_31").id)],
            order="id",
        )

        self.start_tour(
            f"/pos/ui?config_id={self.main_pos_config.id}",
            "PosOrderToSaleOrderTour",
            login="accountman",
        )

        after_orders = self.env["sale.order"].search(
            [("partner_id", "=", self.env.ref("base.res_partner_address_31").id)],
            order="id",
        )

        self.assertEqual(len(before_orders) + 1, len(after_orders))

        order = after_orders[-1]

        self.assertEqual(order.amount_total, 3.2)
        self.assertEqual(order.state, "sale")
        self.assertEqual(order.delivery_status, "full")
        self.assertEqual(order.invoice_status, "invoiced")
