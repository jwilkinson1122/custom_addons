from odoo.tests.common import TransactionCase


class TestPodiatryAdministrationFlag(TransactionCase):

    def setUp(self):
        super(TestPodiatryAdministrationFlag, self).setUp()
        self.Flag = self.env["podiatry.flag"]
        self.Partner = self.env["res.partner"]
        self.FlagCategory = self.env["podiatry.flag.category"]

    def test_service(self):
        category = self.FlagCategory.create({"name": "Category"})
        patient = self.Patient.create({"name": "Patient", "is_patient": True})

        self.assertEqual(patient.patient_flag_count, 0)

        # Create flags
        patient_flag = self.Flag.create({
            "patient_id": patient.id,
            "description": "Description",
            "category_id": category.id
        })

        # Check podiatry_flag_count after creating flags
        self.assertEqual(patient.patient_flag_count, 1)

        # Check action_view_flags results
        self.assertEqual(patient.action_view_patient_flags()["res_id"], patient_flag.id)

        # Check if flags are active
        self.assertTrue(patient_flag.active)

        # Check if closure_date is set
        self.assertFalse(patient_flag.closure_date)

        # Close flags
        patient_flag.close()

        # Check if flags are inactive after closing
        self.assertFalse(patient_flag.active)

        # Check if closure_date is set after closing
        self.assertTrue(patient_flag.closure_date)

        # Check display_name of flags
        self.assertEqual(patient_flag.display_name, "[{}] {}".format(patient_flag.internal_identifier, category.name))
