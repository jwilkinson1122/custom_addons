

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestPodiatryCommission(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.specialty = cls.env["pod.specialty"].create(
            {"name": "Trauma", "description": "Traumatology", "code": "TRA"}
        )
        cls.specialty.sequence_number_next = 21
        cls.practitioner = cls.env.ref("pod_administration_practitioner.practitioner")
        cls.ict = cls.env.ref("pod_administration_practitioner.ict")

    def test_create_practitioner_practitioner(self):
        practitioner = self.env["res.partner"].create(
            {
                "name": "Practitioner",
                "is_practitioner": True,
                "practitioner_role_id": self.practitioner.id,
                "specialty_id": self.specialty.id,
            }
        )
        self.assertEqual(practitioner.ref, "TRA021")
        self.assertEqual(
            practitioner.specialty_id.id, practitioner.specialty_ids.ids[0]
        )
        self.assertEqual(
            practitioner.practitioner_role_id.id,
            practitioner.practitioner_role_ids.ids[0],
        )
        self.specialty._compute_seq_number_next()
        self.assertEqual(self.specialty.sequence_number_next, 22)

        self.assertEqual(self.specialty, practitioner.specialty_ids)

    def test_create_practitioner_practitioner_search(self):
        practitioner = self.env["res.partner"].create(
            {
                "name": "Practitioner",
                "is_practitioner": True,
                "practitioner_role_ids": [(4, self.practitioner.id)],
                "specialty_ids": [(4, self.specialty.id)],
            }
        )
        self.assertEqual(self.specialty, practitioner.specialty_id)
        pracs = self.env["res.partner"].search(
            [("specialty_id", "=", self.specialty.id)]
        )
        self.assertEqual(pracs, practitioner)

    def test_create_practitioner_it(self):
        practitioner = self.env["res.partner"].create(
            {
                "name": "Practitioner",
                "is_practitioner": True,
                "practitioner_role_ids": [(4, self.ict.id)],
            }
        )
        self.assertFalse(practitioner.ref)
        self.assertEqual(self.ict, practitioner.practitioner_role_id)
        self.assertEqual(self.ict, practitioner.practitioner_role_ids)

    def test_constrain_01(self):
        practitioner = self.env["res.partner"].create(
            {
                "name": "Practitioner",
                "is_practitioner": True,
                "practitioner_role_id": self.practitioner.id,
                "specialty_id": self.specialty.id,
            }
        )
        with self.assertRaises(ValidationError):
            practitioner.practitioner_role_ids |= self.ict

    def test_write_new_ref(self):
        practitioner = self.env["res.partner"].create(
            {
                "name": "Practitioner",
            }
        )
        self.assertFalse(practitioner.ref)
        practitioner.write(
            {
                "is_practitioner": True,
                "practitioner_role_id": self.practitioner.id,
                "specialty_id": self.specialty.id,
            }
        )
        self.assertTrue(practitioner.ref)
        self.assertEqual(practitioner.ref, "TRA021")

    def test_write_keep_ref(self):
        practitioner = self.env["res.partner"].create(
            {"name": "Practitioner", "ref": "MY_REF"}
        )
        practitioner.write(
            {
                "is_practitioner": True,
                "practitioner_role_id": self.practitioner.id,
                "specialty_id": self.specialty.id,
            }
        )
        self.assertNotEqual(practitioner.ref, "TRA021")
