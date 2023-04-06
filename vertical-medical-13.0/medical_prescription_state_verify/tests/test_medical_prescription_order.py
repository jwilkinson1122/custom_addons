# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMedicalPrescriptionOrder(TransactionCase):

    def setUp(self):
        super(TestMedicalPrescriptionOrder, self).setUp()

        module = 'medical_prescription_state_verify'
        self.test_order = self.env.ref(
            module + '.medical_prescription_order_1_demo'
        )
        self.test_line = self.env.ref(
            module + '.medical_prescription_order_line_1_demo'
        )

        self.state_module = 'medical_prescription_state'
        self.verified_rx_state = self.env.ref(
            self.state_module + '.prescription_order_state_verified'
        )
        self.unverified_rx_state = self.env.ref(
            self.state_module + '.prescription_order_state_unverified'
        )
        self.cancelled_rx_state = self.env.ref(
            self.state_module + '.prescription_order_state_cancelled'
        )
        self.exception_line_state = self.env.ref(
            self.state_module + '.prescription_order_line_state_exception'
        )

    def test_write_no_content_changes_verified_rx(self):
        self.test_order.stage_id = self.verified_rx_state

        with self.assertRaisesRegexp(ValidationError, 'edit'):
            self.test_order.name = 'Test Name'

    def test_write_restricted_state_changes_verified_rx(self):
        self.test_order.stage_id = self.verified_rx_state

        with self.assertRaisesRegexp(ValidationError, 'move'):
            self.test_order.stage_id = self.unverified_rx_state

    def test_write_allowed_state_changes_verified_rx(self):
        self.test_order.stage_id = self.verified_rx_state

        try:
            self.test_order.stage_id = self.cancelled_rx_state
        except ValidationError:
            self.fail('A ValidationError was raised and should not have been.')

    def test_write_no_limits_unverified_rx(self):
        self.test_order.stage_id = self.unverified_rx_state

        try:
            self.test_order.name = 'Test Name'
            self.test_order.stage_id = self.verified_rx_state
        except ValidationError:
            self.fail('A ValidationError was raised and should not have been.')

    def test_write_line_to_hold_when_change_to_verified(self):
        self.test_order.stage_id = self.verified_rx_state

        hold_line_state = self.env.ref(
            self.state_module + '.prescription_order_line_state_hold'
        )
        self.assertEqual(self.test_line.stage_id, hold_line_state)

    def test_write_line_to_exception_when_change_to_cancelled(self):
        self.test_order.stage_id = self.cancelled_rx_state

        self.assertEqual(self.test_line.stage_id, self.exception_line_state)

    def test_write_line_to_exception_when_change_to_exception(self):
        exception_rx_state = self.env.ref(
            self.state_module + '.prescription_order_state_exception'
        )
        self.test_order.stage_id = exception_rx_state

        self.assertEqual(self.test_line.stage_id, self.exception_line_state)
