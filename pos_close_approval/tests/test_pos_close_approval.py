# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPosCloseApproval(TransactionCase):
    def setUp(self):
        super(TestPosCloseApproval, self).setUp()
        self.pos_config = self.env["pos.config"].create({"name": "PoS config"})
        self.session = False

    def _open_session(self):
        self.pos_config.open_session_cb()
        self.session = self.pos_config.current_session_id
        self.session.action_pos_session_open()

    def test_unicity(self):
        self._open_session()
        with self.assertRaises(ValidationError):
            self.env["pos.session"].create(
                {"config_id": self.pos_config.id, "user_id": self.env.uid}
            )

    def test_unicity_with_approval(self):
        self.pos_config.requires_approval = True
        self._open_session()
        with self.assertRaises(ValidationError):
            self.env["pos.session"].create(
                {"config_id": self.pos_config.id, "user_id": self.env.uid}
            )

    def test_unicity_when_closed(self):
        self.pos_config.requires_approval = True
        self._open_session()
        self.session.action_pos_session_closing_control()
        self.assertEqual(self.session.state, "pending_approval")
        session = self.env["pos.session"].create(
            {"config_id": self.pos_config.id, "user_id": self.env.uid}
        )
        self.assertTrue(session)

    def test_normal_closing(self):
        self._open_session()
        self.session.action_pos_session_closing_control()
        self.session.flush()
        self.assertEqual(self.session.state, "closed")

    def test_validation(self):
        self.pos_config.requires_approval = True
        self._open_session()
        self.session = self.pos_config.current_session_id
        self.session.action_pos_session_open()
        self.session.action_pos_session_closing_control()
        self.assertEqual(self.session.state, "pending_approval")
        self.pos_config.open_session_cb()
        self.assertTrue(self.pos_config.current_session_id)
        self.session.action_pos_session_approve()
        self.assertEqual(self.session.state, "closed")

    def test_wizard(self):
        account = self.env["account.account"].create(
            {
                "company_id": self.pos_config.company_id.id,
                "name": "Account",
                "code": "CODE",
                "user_type_id": self.ref("account.data_account_type_prepayments"),
            }
        )
        self._open_session()
        wizard = (
            self.env["cash.box.out"]
            .with_context(active_model="pos.session", active_ids=self.session.ids)
            .create({"amount": 10, "name": "Out"})
        )
        wizard.run()
        self.assertGreater(
            self.session.statement_ids.balance_end,
            self.session.statement_ids.balance_start,
        )
        wizard = (
            self.env["cash.box.out"]
            .with_context(active_model="pos.session", active_ids=self.session.ids)
            .create({"amount": -10, "name": "Out"})
        )
        wizard.run()
        self.assertEqual(
            self.session.statement_ids.balance_end,
            self.session.statement_ids.balance_start,
        )
        statement = self.session.statement_ids
        line = statement.line_ids[0]
        self.env["account.bank.statement.line.account"].with_context(
            active_model="account.bank.statement.line", active_ids=line.ids
        ).create({"account_id": account.id}).run()
        self.assertEqual(account.id, line.account_id.id)
