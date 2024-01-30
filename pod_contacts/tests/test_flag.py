from odoo.tests.common import TransactionCase


class TestPodiatryAdministrationFlag(TransactionCase):

    def setUp(self):
        super(TestPodiatryAdministrationFlag, self).setUp()
        self.Flag = self.env["pod.flag"]
        self.Partner = self.env["res.partner"]
        self.Patient = self.env["pod.patient"]
        self.FlagCategory = self.env["pod.flag.category"]

    def test_service(self):
        category = self.FlagCategory.create({"name": "Category"})
        # account = self.Partner.create({"name": "Practice", "is_company": True})
        # practitioner = self.Partner.create({"name": "Practitioner", "is_practitioner": True})
        patient = self.Patient.create({"name": "Patient"})

        # self.assertEqual(account.account_flag_count, 0)
        # self.assertEqual(practitioner.practitioner_flag_count, 0)
        self.assertEqual(patient.patient_flag_count, 0)

        # Create flags
        # account_flag = self.Flag.create({
        #     "account_id": account.id,
        #     "description": "Description",
        #     "category_id": category.id
        # })
        # practitioner_flag = self.Flag.create({
        #     "pod_practitioner_id": practitioner.id,
        #     "description": "Description",
        #     "category_id": category.id
        # })
        patient_flag = self.Flag.create({
            "pod_patient_id": patient.id,
            "description": "Description",
            "category_id": category.id
        })

        # Check pod_flag_count after creating flags
        # self.assertEqual(account.account_flag_count, 1)
        # self.assertEqual(practitioner.practitioner_flag_count, 1)
        self.assertEqual(patient.patient_flag_count, 1)

        # Check action_view_flags results
        # self.assertEqual(account.action_view_account_flags()["res_id"], account_flag.id)
        # self.assertEqual(practitioner.action_view_practitioner_flags()["res_id"], practitioner_flag.id)
        self.assertEqual(patient.action_view_patient_flags()["res_id"], patient_flag.id)

        # Check if flags are active
        # self.assertTrue(account_flag.active)
        # self.assertTrue(practitioner_flag.active)
        self.assertTrue(patient_flag.active)

        # Check if closure_date is set
        # self.assertFalse(account_flag.closure_date)
        # self.assertFalse(practitioner_flag.closure_date)
        self.assertFalse(patient_flag.closure_date)

        # Close flags
        # account_flag.close()
        # practitioner_flag.close()
        patient_flag.close()

        # Check if flags are inactive after closing
        # self.assertFalse(account_flag.active)
        # self.assertFalse(practitioner_flag.active)
        self.assertFalse(patient_flag.active)

        # Check if closure_date is set after closing
        # self.assertTrue(account_flag.closure_date)
        # self.assertTrue(practitioner_flag.closure_date)
        self.assertTrue(patient_flag.closure_date)

        # Check display_name of flags
        # self.assertEqual(account_flag.display_name, "[{}] {}".format(account_flag.pod_internal_identifier, category.name))
        # self.assertEqual(practitioner_flag.display_name, "[{}] {}".format(practitioner_flag.pod_internal_identifier, category.name))
        self.assertEqual(patient_flag.display_name, "[{}] {}".format(patient_flag.pod_internal_identifier, category.name))
