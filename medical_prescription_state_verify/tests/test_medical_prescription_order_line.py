# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMedicalPrescriptionOrderLine(TransactionCase):

    def setUp(self):
        super(TestMedicalPrescriptionOrderLine, self).setUp()

        module = 'medical_prescription_state_verify'
        self.test_line = self.env.ref(
            module + '.medical_prescription_order_line_1_demo'
        )

        self.state_module = 'medical_prescription_state'
        self.hold_line_state = self.env.ref(
            self.state_module + '.prescription_order_line_state_hold'
        )

    def test_write_restricted_state_changes_verified_line(self):
        self.test_line.stage_id = self.hold_line_state
        unverified_line_state = self.env.ref(
            self.state_module + '.prescription_order_line_state_unverified'
        )

        with self.assertRaises(ValidationError):
            self.test_line.stage_id = unverified_line_state

    def test_write_allowed_state_changes_verified_line(self):
        self.test_line.stage_id = self.hold_line_state
        exception_line_state = self.env.ref(
            self.state_module + '.prescription_order_line_state_exception'
        )

        try:
            self.test_line.stage_id = exception_line_state
        except ValidationError:
            self.fail('A ValidationError was raised and should not have been.')

    def test_write_no_state_change_restrictions_unverified_line(self):
        complete_line_state = self.env.ref(
            self.state_module + '.prescription_order_line_state_complete'
        )

        try:
            self.test_line.stage_id = complete_line_state
        except ValidationError:
            self.fail('A ValidationError was raised and should not have been.')
