from odoo import exceptions
from odoo.tests import common


class TestWizard(common.SingleTransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestWizard, self).setUp(*args, **kwargs)
        # Setup test data
        admin_user = self.env.ref('base.user_admin')
        self.Bookout = self.env["practice.bookout"]\
            .with_user(admin_user)
        self.Wizard = self.env['practice.bookout.massmessage']\
            .with_user(admin_user)
        a_practitioner = self.env['practice.practitioner']\
            .create({'partner_id': admin_user.partner_id.id})
        self.bookout0 = self.Bookout\
            .create({'practitioner_id': a_practitioner.id})

    def test_01_button_send(self):
        """Send button should create messages on Bookouts"""
        count_before = len(self.bookout0.message_ids)
        Wizard0 = self.Wizard\
            .with_context(active_ids=self.bookout0.ids)
        wizard0 = Wizard0.create({
            "message_subject": "Hello",
            "message_body": "This is a message.",
        })
        wizard0.button_send()
        count_after = len(self.bookout0.message_ids)
        self.assertEqual(
            count_before + 1,
            count_after,
            "Expected one additional message in the Bookout.",
        )

    def test_02_button_send_empty_body(self):
        """Send button errors on empty body message"""
        Wizard0 = self.Wizard\
            .with_context(active_ids=self.bookout0.ids)
        wizard0 = Wizard0.create({})
        with self.assertRaises(exceptions.UserError) as e:
            wizard0.button_send()
