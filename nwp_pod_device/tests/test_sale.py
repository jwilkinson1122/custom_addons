from odoo.tests.common import Form

from odoo.addons.nwp_pod_pos.tests import common


class TestNWPPodiatryCommission(common.PodiatrySavePointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category.write({"category_product_id": cls.service.id})
        cls.product_extra = cls.env["product.product"].create(
            {
                "type": "consu",
                "categ_id": cls.category.id,
                "name": "Clinical material",
                "is_device": True,
                "lst_price": 10.0,
                "taxes_id": [(6, 0, cls.tax.ids)],
            }
        )

    def test_careplan_sale_device(self):
        self.action.is_billable = False
        encounter, careplan, group = self.create_careplan_and_group(self.agreement_line)
        groups = self.env["pod.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertTrue(groups)
        device_requests = self.env["pod.device.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertEqual(careplan.state, "draft")
        self.assertFalse(device_requests.filtered(lambda r: r.is_billable))
        self.assertTrue(
            groups.filtered(lambda r: r.child_model == "pod.device.request")
        )
        self.assertTrue(
            groups.filtered(
                lambda r: (r.is_sellable_insurance or r.is_sellable_private)
                and r.child_model == "pod.device.request"
            )
        )
        self.assertTrue(
            groups.filtered(
                lambda r: r.is_billable
                and r.child_model == "pod.device.request"
            )
        )
        self.assertFalse(encounter.device_item_ids)
        self.env["pod.encounter.device"].create(
            {
                "pod_id": encounter.id,
                "product_id": self.product_03.id,
                "location_id": self.location.id,
            }
        ).run()
        self.assertEqual(1, len(encounter.device_item_ids))
        self.assertTrue(encounter.device_item_ids)
        self.env["pod.encounter.device"].create(
            {
                "pod_id": encounter.id,
                "product_id": self.product_03.id,
                "location_id": self.location.id,
            }
        ).run()
        self.assertTrue(device_requests)
        self.assertFalse(device_requests.mapped("device_administration_ids"))
        self.env["wizard.pod.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertTrue(encounter.sale_order_ids)
        self.assertGreater(self.session.encounter_count, 0)
        self.assertGreater(self.session.sale_order_count, 0)
        self.assertEqual(self.session.action_view_encounters()["res_id"], encounter.id)
        device_requests.refresh()
        self.assertTrue(device_requests.mapped("device_administration_ids"))
        self.env["wizard.pod.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "payment_method_id": self.session.payment_method_ids.ids[0],
            }
        ).run()
        self.assertTrue(
            self.env["stock.picking"].search([("encounter_id", "=", encounter.id)])
        )

    def test_onchange_device(self):
        self.action.is_billable = False
        encounter, careplan, group = self.create_careplan_and_group(self.agreement_line)
        with Form(
            self.env["pod.device.item"].with_context(
                default_encounter_id=encounter.id,
            )
        ) as item:
            item.product_id = self.product_03
            self.assertEqual(10, item.price)
            item.qty = 10
            self.assertEqual(100, item.amount)
            item.location_id = self.location

    def test_bom(self):
        encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient_01.id, "practice_id": self.practice.id}
        )
        self.env["mrp.bom"].create(
            {
                "product_id": self.product_03.id,
                "product_tmpl_id": self.product_03.product_tmpl_id.id,
                "type": "phantom",
                "bom_line_ids": [(0, 0, {"product_id": self.product_extra.id})],
            }
        )
        self.env["pod.encounter.device"].create(
            {
                "pod_id": encounter.id,
                "product_id": self.product_03.id,
                "location_id": self.location.id,
            }
        ).run()
        self.assertEqual(2, len(encounter.device_item_ids))
        self.assertEqual(
            1,
            len(encounter.device_item_ids.filtered(lambda r: r.is_phantom)),
        )
