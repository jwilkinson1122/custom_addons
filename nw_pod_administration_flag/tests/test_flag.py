from odoo.tests.common import TransactionCase


class TestNWPodiatryAdministrationFlag(TransactionCase):
    def test_service(self):
        category = self.env["pod.flag.category"].create(
            {"name": "Category", "icon": "fa fa-flag"}
        )
        patient = self.env["pod.patient"].create({"name": "Patient"})
        self.assertEqual(patient.pod_flag_count, 0)
        flag = self.env["pod.flag"].create(
            {
                "patient_id": patient.id,
                "description": "Description",
                "category_id": category.id,
            }
        )
        self.assertEqual(patient.pod_flag_count, 1)
        action = patient.action_view_flags()
        self.assertEqual(action["res_id"], flag.id)
        self.assertTrue(flag.active)
        self.assertFalse(flag.closure_date)
        flag.close()
        self.assertFalse(flag.active)
        self.assertTrue(flag.closure_date)
        self.assertEqual(
            flag.display_name,
            "[{}] {}".format(flag.internal_identifier, category.name),
        )
        self.assertTrue(flag.level)
        self.assertTrue(flag.flag)
        self.assertEqual(flag.flag, "fa fa-flag text-success")
