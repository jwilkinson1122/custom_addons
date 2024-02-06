from odoo.tests.common import TransactionCase


class TestPrescriptionAdministrationFlag(TransactionCase):

    def setUp(self):
        super(TestPrescriptionAdministrationFlag, self).setUp()
        self.Flag = self.env["prescription.flag"]
        self.Partner = self.env["res.partner"]
        self.Patient = self.env["prescription.patient"]
        self.FlagCategory = self.env["prescription.flag.category"]

    def test_service(self):
        category = self.FlagCategory.create({"name": "Category"})
        # practice = self.Partner.create({"name": "Practice", "is_company": True})
        # practitioner = self.Partner.create({"name": "Practitioner", "is_practitioner": True})
        patient = self.Patient.create({"name": "Patient"})

        # self.assertEqual(practice.practice_flag_count, 0)
        # self.assertEqual(practitioner.practitioner_flag_count, 0)
        self.assertEqual(patient.patient_flag_count, 0)

        # Create flags
        # practice_flag = self.Flag.create({
        #     "practice_id": practice.id,
        #     "description": "Description",
        #     "category_id": category.id
        # })
        # practitioner_flag = self.Flag.create({
        #     "practitioner_id": practitioner.id,
        #     "description": "Description",
        #     "category_id": category.id
        # })
        patient_flag = self.Flag.create({
            "patient_id": patient.id,
            "description": "Description",
            "category_id": category.id
        })

        # Check prescription_flag_count after creating flags
        # self.assertEqual(practice.practice_flag_count, 1)
        # self.assertEqual(practitioner.practitioner_flag_count, 1)
        self.assertEqual(patient.patient_flag_count, 1)

        # Check action_view_flags results
        # self.assertEqual(practice.action_view_practice_flags()["res_id"], practice_flag.id)
        # self.assertEqual(practitioner.action_view_practitioner_flags()["res_id"], practitioner_flag.id)
        self.assertEqual(patient.action_view_patient_flags()["res_id"], patient_flag.id)

        # Check if flags are active
        # self.assertTrue(practice_flag.active)
        # self.assertTrue(practitioner_flag.active)
        self.assertTrue(patient_flag.active)

        # Check if closure_date is set
        # self.assertFalse(practice_flag.closure_date)
        # self.assertFalse(practitioner_flag.closure_date)
        self.assertFalse(patient_flag.closure_date)

        # Close flags
        # practice_flag.close()
        # practitioner_flag.close()
        patient_flag.close()

        # Check if flags are inactive after closing
        # self.assertFalse(practice_flag.active)
        # self.assertFalse(practitioner_flag.active)
        self.assertFalse(patient_flag.active)

        # Check if closure_date is set after closing
        # self.assertTrue(practice_flag.closure_date)
        # self.assertTrue(practitioner_flag.closure_date)
        self.assertTrue(patient_flag.closure_date)

        # Check display_name of flags
        # self.assertEqual(practice_flag.display_name, "[{}] {}".format(practice_flag.internal_identifier, category.name))
        # self.assertEqual(practitioner_flag.display_name, "[{}] {}".format(practitioner_flag.internal_identifier, category.name))
        self.assertEqual(patient_flag.display_name, "[{}] {}".format(patient_flag.internal_identifier, category.name))
