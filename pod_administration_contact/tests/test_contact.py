
from odoo.tests.common import TransactionCase


class TestPodContact(TransactionCase):
    def setUp(self):
        super(TestPodContact, self).setUp()
        self.pod_user_group = self.env.ref(
            "pod_base.group_pod_configurator"
        )
        self.pod_user = self._create_user(
            "pod_user", self.pod_user_group.id
        )
        self.patient_model = self.env["pod.patient"]
        self.location_model = self.env["res.partner"]
        self.contact_model = self.env["pod.contact"]
        self.patient_1 = self._create_patient()
        self.location_1 = self._create_location()

    def _create_patient(self):
        return self.patient_model.create(
            {"name": "Test patient", "gender": "female"}
        )

    def _create_location(self):
        return self.location_model.create(
            {"name": "Test location", "is_location": True}
        )

    def _create_user(self, name, group_ids):
        return (
            self.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": name,
                    "password": "demo",
                    "login": name,
                    "email": "@".join([name, "@test.com"]),
                    "groups_id": [(6, 0, [group_ids])],
                }
            )
        )

    def _create_contact(self, state):
        return self.contact_model.create(
            {
                "name": "test contact",
                "patient_id": self.patient_1.id,
                "location_id": self.location_1.id,
                "state": state,
            }
        )

    def test_security(self):
        contact_vals = {
            "name": "test contact",
            "patient_id": self.patient_1.id,
            "location_id": self.location_1.id,
            "state": "arrived",
        }
        contact = self.contact_model.with_user(self.pod_user).create(
            contact_vals
        )
        self.assertNotEquals(contact, False)

    def test_contact_complete_flow(self):
        contact_vals = {
            "name": "test contact",
            "patient_id": self.patient_1.id,
            "location_id": self.location_1.id,
            "state": "planned",
        }
        contact = self.contact_model.create(contact_vals)
        self.assertEqual(contact.state, "planned")
        contact.planned2arrived()
        self.assertTrue(contact.is_editable)
        self.assertEqual(contact.state, "arrived")
        contact.arrived2inprogress()
        self.assertFalse(contact.is_editable)
        self.assertEqual(contact.state, "in-progress")
        contact.inprogress2onleave()
        self.assertFalse(contact.is_editable)
        self.assertEqual(contact.state, "onleave")
        contact.onleave2finished()
        self.assertFalse(contact.is_editable)
        self.assertEqual(contact.state, "finished")

    def test_contact_cancelled_flow(self):
        # planned2cancelled
        contact_1 = self._create_contact("planned")
        self.assertEqual(contact_1.state, "planned")
        contact_1.planned2cancelled()
        self.assertFalse(contact_1.is_editable)
        self.assertEqual(contact_1.state, "cancelled")
        # arrived2cancelled
        contact_2 = self._create_contact("arrived")
        self.assertEqual(contact_2.state, "arrived")
        contact_2.arrived2cancelled()
        self.assertFalse(contact_2.is_editable)
        self.assertEqual(contact_2.state, "cancelled")
        # inprogress2cancelled
        contact_3 = self._create_contact("in-progress")
        self.assertEqual(contact_3.state, "in-progress")
        contact_3.inprogress2cancelled()
        self.assertFalse(contact_3.is_editable)
        self.assertEqual(contact_3.state, "cancelled")
        # onleave2cancelled
        contact_4 = self._create_contact("onleave")
        self.assertEqual(contact_4.state, "onleave")
        contact_4.onleave2cancelled()
        self.assertFalse(contact_4.is_editable)
        self.assertEqual(contact_4.state, "cancelled")
