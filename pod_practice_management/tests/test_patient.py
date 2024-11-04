from odoo.tests import TransactionCase, tagged, Form
from odoo import fields, Command
from datetime import timedelta


@tagged("-at_install", "post_install")
class TestPatient(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        organization = cls.env["res.partner"].create(
            {"name": "Test Org"},
        )
        practice1 = cls.env["podiatry.practice"].create(
            {
                "name": "Test practice",
                "parent_id": organization.id,
            }
        )
        coach = cls.env["podiatry.practice.staff"].create(
            {
                "partner_id": cls.env["res.partner"]
                .create(
                    {
                        "name": "Test Coach",
                    }
                )
                .id,
                "practice_id": practice1.id,
                "role": "head_coach",
            }
        )
        patient1 = cls.env["podiatry.patient"].create(
            {
                "first_name": "Test",
                "last_name": "Patient 1",
                "practice_ids": [Command.set(practice1.ids)],
                "date_of_birth": fields.Date.today() - timedelta(days=18 * 365),
            }
        )
        patient1_pathology = cls.env["podiatry.patient.pathology"].create(
            {
                "patient_id": patient1.id,
            }
        )
        patient2 = cls.env["podiatry.patient"].create(
            {
                "first_name": "Test",
                "last_name": "Patient2",
                "practice_ids": [Command.set(practice1.ids)],
                "date_of_birth": fields.Date.today() - timedelta(days=21 * 365),
            }
        )
        patient2_pathology = cls.env["podiatry.patient.pathology"].create(
            {
                "patient_id": patient2.id,
            }
        )
        (
            cls.organization,
            cls.practice1,
            cls.coach,
            cls.patient1,
            cls.patient1_pathology,
            cls.patient2,
            cls.patient2_pathology,
        ) = (
            organization,
            practice1,
            coach,
            patient1,
            patient1_pathology,
            patient2,
            patient2_pathology,
        )

    def test_adding_staff_adds_follower_to_patient_and_pathology(self):
        therapist = self.env["podiatry.practice.staff"].create(
            {
                "practice_id": self.practice1.id,
                "partner_id": self.env["res.partner"]
                .create(
                    {"name": "Tester"},
                )
                .id,
                "role": "therapist",
            }
        )

        therapist = therapist.partner_id
        self.assertIn(therapist, self.patient1.message_partner_ids)
        self.assertIn(therapist, self.patient2.message_partner_ids)
        self.assertIn(therapist, self.patient1_pathology.message_partner_ids)
        self.assertIn(therapist, self.patient2_pathology.message_partner_ids)

    def test_removing_staff_removes_follower_from_patient_and_pathology(self):
        coach = self.coach.partner_id
        self.practice1.staff_ids = False
        self.assertNotIn(coach, self.patient1.message_partner_ids)
        self.assertNotIn(coach, self.patient1_pathology.message_partner_ids)
        self.assertNotIn(coach, self.patient2.message_partner_ids)
        self.assertNotIn(coach, self.patient2_pathology.message_partner_ids)

    def test_deleting_practice_removes_follower_from_patient_and_pathology(self):
        coach = self.coach.partner_id
        self.practice1.unlink()
        self.assertNotIn(coach, self.patient1.message_partner_ids)
        self.assertNotIn(coach, self.patient1_pathology.message_partner_ids)
        self.assertNotIn(coach, self.patient2.message_partner_ids)
        self.assertNotIn(coach, self.patient2_pathology.message_partner_ids)

    def test_adding_second_practice_subscribes_new_staff(self):
        practice2, therapist, coach = self._generate_second_practice_and_staff()

        practice2.patient_ids = self.patient1

        self.assertIn(therapist, self.patient1.message_partner_ids)
        self.assertIn(coach, self.patient1.message_partner_ids)
        self.assertIn(therapist, self.patient1_pathology.message_partner_ids)
        self.assertIn(coach, self.patient1_pathology.message_partner_ids)
        self.assertEqual(len(self.patient1_pathology.message_partner_ids), 2)
        self.assertEqual(len(self.patient1.message_partner_ids), 2)

    def test_creating_patient_in_practice_assigns_followers(self):
        patient = self.env["podiatry.patient"].create(
            {
                "first_name": "Test",
                "last_name": "Patient",
                "date_of_birth": fields.Date.today() - timedelta(days=365 * 20),
                "practice_ids": [(6, 0, self.practice1.ids)],
            }
        )

        cp_id = self.coach.partner_id
        self.assertIn(cp_id, patient.message_partner_ids)

        pathology = self.env["podiatry.patient.pathology"].create(
            {
                "patient_id": patient.id,
                "diagnosis": "Something",
            }
        )
        self.assertIn(cp_id, pathology.message_partner_ids)

    def test_removing_second_practice_correctly_adjusts_staff(self):
        """Tests both removing from the practice side and from the patient side."""
        practice2, therapist, coach = self._generate_second_practice_and_staff()
        self.patient1.write({"practice_ids": [Command.link(practice2.id)]})
        self.assertIn(self.patient1, practice2.patient_ids)
        self.assertIn(therapist, self.patient1.message_partner_ids)

        practice2.write({"patient_ids": [Command.unlink(self.patient1.id)]})

        self.assertNotIn(self.patient1, practice2.patient_ids)
        self.assertEqual(self.patient1.message_partner_ids, coach)
        self.assertEqual(self.patient1_pathology.message_partner_ids, coach)

        self.patient1.write({"practice_ids": [Command.link(practice2.id)]})

        self.assertIn(self.patient1, practice2.patient_ids)
        self.assertIn(therapist, self.patient1.message_partner_ids)

        self.patient1.write({"practice_ids": [Command.unlink(practice2.id)]})

        self.assertNotIn(self.patient1, practice2.patient_ids)
        self.assertEqual(self.patient1.message_partner_ids, coach)
        self.assertEqual(self.patient1_pathology.message_partner_ids, coach)

    def test_adding_patient_pathology_sets_followers(self):
        pathology2 = self.env["podiatry.patient.pathology"].create(
            {
                "patient_id": self.patient1.id,
                "diagnosis": "some other pathology",
            }
        )

        self.assertEqual(pathology2.message_partner_ids, self.coach.partner_id)

    def _generate_second_practice_and_staff(self):
        practice2 = self.env["podiatry.practice"].create(
            {
                "parent_id": self.organization.id,
                "name": "Test practice 2",
            }
        )
        therapist = (
            self.env["podiatry.practice.staff"]
            .create(
                {
                    "practice_id": practice2.id,
                    "partner_id": self.env["res.partner"]
                    .create(
                        {"name": "Tester"},
                    )
                    .id,
                    "role": "therapist",
                }
            )
            .partner_id
        )
        coach = (
            self.env["podiatry.practice.staff"]
            .create(
                {
                    "practice_id": practice2.id,
                    "partner_id": self.coach.partner_id.id,
                    "role": "coach",
                }
            )
            .partner_id
        )
        return practice2, therapist, coach

    def test_changing_patient_name_changes_on_partner(self):
        new_last_name = "New last name"
        new_first_name = "New first name"
        with Form(self.patient1) as patient:
            patient.last_name = new_last_name
            patient.first_name = new_first_name
        self.assertEqual(
            self.patient1.partner_id.name, " ".join([new_first_name, new_last_name])
        )
