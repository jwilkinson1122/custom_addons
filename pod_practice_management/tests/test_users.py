from odoo.tests import TransactionCase, tagged, Form
from odoo import Command


@tagged("-at_install", "post_install")
class TestUsers(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_add_practice_access_to_user(self):
        user = self.env["res.users"].create(
            {
                "name": "test",
                "login": "test",
                "password": "test",
                "groups_id": [
                    Command.set(
                        self.env.ref(
                            "pod_practice_management.group_podiatry_practice_physician"
                        ).ids
                    )
                ],
            }
        )
        practice = self.env["podiatry.practice"].create(
            {
                "name": "Test",
            }
        )

        self.assertNotIn(user, practice.staff_ids.user_ids)
        user.write({"accessible_practice_ids": [Command.link(practice.id)]})
        # user._inverse_accessible_practice_ids()
        self.assertIn(user, practice.staff_ids.user_ids)
