
from odoo.tests import common


class TestInstruction(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env["sale.order"]
        cls.product_set = cls.env["product.set"]
        cls.partner1 = cls.env.ref("base.res_partner_1")
        cls.partner2 = cls.env.ref("base.res_partner_2")

    def test_instruction_count_no_typology_match(self):
        prod_set = self.env.ref("pod_product_set.product_set_services")
        for __ in range(2):
            prod_set.copy(default={"partner_id": self.partner1.id})
        for __ in range(4):
            prod_set.copy(default={"partner_id": self.partner2.id})
        self.assertEqual(self.partner1.instructions_count, 0)
        self.assertEqual(self.partner2.instructions_count, 0)

    def test_instruction_count(self):
        prod_set = self.env.ref("pod_product_set.product_set_services")
        vals = {"partner_id": self.partner1.id, "typology": "instruction"}
        for __ in range(2):
            prod_set.copy(default=vals)
        vals = {"partner_id": self.partner2.id, "typology": "instruction"}
        for __ in range(4):
            prod_set.copy(default=vals)
        self.assertEqual(self.partner1.instructions_count, 2)
        self.assertEqual(self.partner2.instructions_count, 4)

    def test_action(self):
        action = self.partner1.action_view_instructions()
        self.assertEqual(
            action["context"],
            {"default_partner_id": self.partner1.id, "default_typology": "instruction"},
        )
        self.assertEqual(
            action["domain"],
            [("partner_id", "in", [self.partner1.id]), ("typology", "=", "instruction")],
        )
        action = self.partner2.action_view_instructions()
        self.assertEqual(
            action["context"],
            {"default_partner_id": self.partner2.id, "default_typology": "instruction"},
        )
        self.assertEqual(
            action["domain"],
            [("partner_id", "in", [self.partner2.id]), ("typology", "=", "instruction")],
        )
