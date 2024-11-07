from odoo.tests import TransactionCase, Form, tagged
from odoo.fields import Date
from datetime import timedelta
from odoo.exceptions import AccessError
from odoo import Command
import logging

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestRights(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create one admin user
        cls.admin_user = cls.env["res.users"].create(
            {
                "name": "Admin User",
                "login": "podiatry_admin",
                "password": "podiatry_admin",
                "groups_id": [
                    Command.set(
                        cls.env.ref(
                            "pod_practice_management.group_res_practice_admin"
                        ).ids,
                    ),
                ],
            }
        )
        # Create one treatment professional user
        cls.internal_user_user = cls.env["res.users"].create(
            {
                "name": "Internal User",
                "login": "internal_user",
                "password": "internal_user",
                "groups_id": [
                    Command.set(
                        cls.env.ref(
                            "pod_practice_management.group_res_practice_internal_user"
                        ).ids,
                    ),
                ],
            }
        )
        # _logger.info(
        #     f"Treatment Pro Groups: "
        #     f"{cls.internal_user_user.groups_id.mapped('name')}"
        # )

    def test_treatment_pro_has_access_only_to_contacted_practices(self):
        """A treatment professional should only have access to practices and,
        by extension, patients for which they are a practice contact member."""
        practice, patients = self._generate_practice_with_patient(self.admin_user)
        with self.assertRaises(AccessError):
            Form(
                self.env["res.practice"]
                .with_user(self.internal_user_user)
                .browse(practice.id)
            )
        with self.assertRaises(AccessError):
            Form(
                self.env["res.patient"]
                .with_user(self.internal_user_user)
                .browse(patients[0].id)
            )

    def test_treatment_pro_can_remove_patient_from_practice(self):
        practice, patients = self._generate_practice_with_patient(self.admin_user)
        self.env["res.practice.contact"].with_user(self.admin_user).create(
            {
                "practice_id": practice.id,
                "partner_id": self.internal_user_user.partner_id.id,
                "role": "primary_physician",
            }
        )
        # Test removing the patient since we are practice contact
        # Should not throw an error...
        with Form(practice.with_user(self.internal_user_user)) as practice:
            practice.patient_ids.remove(index=0)
        self.assertEqual(len(practice.patient_ids), 1)

    def _generate_practice_with_patient(self, user=None):
        user = user or self.env.user
        practice = (
            self.env["res.practice"]
            .with_user(user)
            .create(
                {
                    "name": "Test Practice",
                }
            )
        )
        patients = (
            self.env["res.patient"]
            .with_user(user)
            .create(
                [
                    {
                        "first_name": "Test",
                        "last_name": "Patient One",
                        "date_of_birth": Date.today() - timedelta(days=-365 * 18),
                        "practice_ids": [(6, 0, practice.ids)],
                    },
                    {
                        "first_name": "Test",
                        "last_name": "Patient Two",
                        "date_of_birth": Date.today() - timedelta(days=-365 * 18),
                        "practice_ids": [(6, 0, practice.ids)],
                    },
                ]
            )
        )
        return practice, patients
