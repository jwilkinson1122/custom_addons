from odoo import exceptions
from odoo.tests import common


class TestWizard(common.SingleTransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestWizard, self).setUp(*args, **kwargs)
        # Setup test data
        admin_user = self.env.ref('base.user_admin')
        self.Prescription = self.env["pod.prescription"]\
            .with_user(admin_user)
        self.Wizard = self.env['pod.prescription.massmessage']\
            .with_user(admin_user)
        a_member = self.env['pod.member']\
            .create({'partner_id': admin_user.partner_id.id})
        self.prescription0 = self.Prescription\
            .create({'member_id': a_member.id})

    def test_01_button_send(self):
        """Send button should create messages on Prescriptions"""
        count_before = len(self.prescription0.message_ids)
        Wizard0 = self.Wizard\
            .with_context(active_ids=self.prescription0.ids)
        wizard0 = Wizard0.create({
            "message_subject": "Hello",
            "message_body": "This is a message.",
        })
        wizard0.button_send()
        count_after = len(self.prescription0.message_ids)
        self.assertEqual(
            count_before + 1,
            count_after,
            "Expected one additional message in the Prescription.",
        )

    def test_02_button_send_empty_body(self):
        """Send button errors on empty body message"""
        Wizard0 = self.Wizard\
            .with_context(active_ids=self.prescription0.ids)
        wizard0 = Wizard0.create({})
        with self.assertRaises(exceptions.UserError) as e:
            wizard0.button_send()
