


from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestPodiatryPatientCreateReport(TransactionCase):
    def setUp(self):
        super(TestPodiatryPatientCreateReport, self).setUp()

        self.patient = self.env["pod.patient"].create(
            {
                "name": "Test Patient",
            }
        )

        self.encounter = self.env["pod.encounter"].create(
            {
                "patient_id": self.patient.id,
                "create_date": datetime.now() - timedelta(days=6),
            }
        )

        self.encounter2 = self.env["pod.encounter"].create(
            {
                "patient_id": self.patient.id,
                "create_date": datetime.now() - timedelta(days=8),
            }
        )

        self.patient.encounter_ids.append(self.encounter1)
        self.patient.encounter_ids.append(self.encounter2)

        self.report = self.env["pod.report"].create(
            {
                "name": "Test Report",
                "template_id": self.env.ref(
                    "pod_fhir.pod_report_template"
                ).id,
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
            }
        )

    def test_check_encounter_date(self):
        self.report.encounter_id.create_date = datetime.now() - timedelta(
            days=8
        )
        self.report.check_encounter_date()
        self.assertTrue(self.report.show_encounter_warning)

    def test_compute_default_encounter(self):
        new_encounter = self.env["pod.encounter"].create(
            {
                "patient_id": self.patient.id,
                "encounter_type": "outpatient",
                "create_date": datetime.now() - timedelta(days=3),
            }
        )

        self.report.patient_id = self.patient.id
        self.report._compute_default_encounter()
        self.assertEqual(self.report.encounter_id, new_encounter)

    def test_generate(self):
        action = self.report.generate()
        self.assertEqual(action["res_model"], "ir.actions.act_window")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["views"][0][1], "form")

    def test_get_last_encounter(self):
        last_encounter = self.patient._get_last_encounter()
        self.assertEqual(last_encounter, self.encounter2)

    def test_get_last_encounter_no_encounters(self):
        self.patient.encounter_ids = []
        with self.assertRaises(ValidationError):
            self.patient._get_last_encounter()
