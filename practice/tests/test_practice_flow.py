# -*- coding: utf-8 -*-


import datetime

from dateutil.relativedelta import relativedelta

from odoo.addons.practice.tests.common import TestPracticeCommon
from odoo.exceptions import ValidationError
from odoo.tests.common import Form
from odoo.tools import mute_logger


class TestPracticeUI(TestPracticeCommon):

    def test_practice_confirmation_partner_sync(self):
        """ Ensure onchange on partner_id is kept for interface, not for computed
        fields. """
        confirmation_form = Form(self.env['practice.confirmation'].with_context(
            default_name='WrongName',
            default_practice_id=self.practice_0.id
        ))
        self.assertEqual(confirmation_form.practice_id, self.practice_0)
        self.assertEqual(confirmation_form.name, 'WrongName')
        self.assertFalse(confirmation_form.email)
        self.assertFalse(confirmation_form.phone)
        self.assertFalse(confirmation_form.mobile)

        # trigger onchange
        confirmation_form.partner_id = self.practice_customer
        self.assertEqual(confirmation_form.name, self.practice_customer.name)
        self.assertEqual(confirmation_form.email, self.practice_customer.email)
        self.assertEqual(confirmation_form.phone, self.practice_customer.phone)
        self.assertEqual(confirmation_form.mobile, self.practice_customer.mobile)

        # save, check record matches Form values
        confirmation = confirmation_form.save()
        self.assertEqual(confirmation.partner_id, self.practice_customer)
        self.assertEqual(confirmation.name, self.practice_customer.name)
        self.assertEqual(confirmation.email, self.practice_customer.email)
        self.assertEqual(confirmation.phone, self.practice_customer.phone)
        self.assertEqual(confirmation.mobile, self.practice_customer.mobile)

        # allow writing on some fields independently from customer config
        confirmation.write({'phone': False, 'mobile': False})
        self.assertFalse(confirmation.phone)
        self.assertFalse(confirmation.mobile)

        # reset partner should not reset other fields
        confirmation.write({'partner_id': False})
        self.assertEqual(confirmation.partner_id, self.env['res.partner'])
        self.assertEqual(confirmation.name, self.practice_customer.name)
        self.assertEqual(confirmation.email, self.practice_customer.email)
        self.assertFalse(confirmation.phone)
        self.assertFalse(confirmation.mobile)

        # update to a new partner not through UI -> update only void feilds
        confirmation.write({'partner_id': self.practice_customer2.id})
        self.assertEqual(confirmation.partner_id, self.practice_customer2)
        self.assertEqual(confirmation.name, self.practice_customer.name)
        self.assertEqual(confirmation.email, self.practice_customer.email)
        self.assertEqual(confirmation.phone, self.practice_customer2.phone)
        self.assertEqual(confirmation.mobile, self.practice_customer2.mobile)


class TestPracticeFlow(TestPracticeCommon):

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_practice_auto_confirm(self):
        """ Basic practice management with auto confirmation """
        # PracticeUser creates a new practice: ok
        test_practice = self.env['practice.practice'].with_user(self.user_practicemanager).create({
            'name': 'TestPractice',
            'auto_confirm': True,
            'date_begin': datetime.datetime.now() + relativedelta(days=-1),
            'date_end': datetime.datetime.now() + relativedelta(days=1),
            'seats_max': 2,
            'seats_limited': True,
        })
        self.assertTrue(test_practice.auto_confirm)

        # PracticeUser create confirmations for this practice
        test_reg1 = self.env['practice.confirmation'].with_user(self.user_practiceuser).create({
            'name': 'TestReg1',
            'practice_id': test_practice.id,
        })
        self.assertEqual(test_reg1.state, 'open', 'Practice: auto_confirmation of confirmation failed')
        self.assertEqual(test_practice.seats_reserved, 1, 'Practice: wrong number of reserved seats after confirmed confirmation')
        test_reg2 = self.env['practice.confirmation'].with_user(self.user_practiceuser).create({
            'name': 'TestReg2',
            'practice_id': test_practice.id,
        })
        self.assertEqual(test_reg2.state, 'open', 'Practice: auto_confirmation of confirmation failed')
        self.assertEqual(test_practice.seats_reserved, 2, 'Practice: wrong number of reserved seats after confirmed confirmation')

        # PracticeUser create confirmations for this practice: too much confirmations
        with self.assertRaises(ValidationError):
            self.env['practice.confirmation'].with_user(self.user_practiceuser).create({
                'name': 'TestReg3',
                'practice_id': test_practice.id,
            })

        # PracticeUser validates confirmations
        test_reg1.action_set_done()
        self.assertEqual(test_reg1.state, 'done', 'Practice: wrong state of attended confirmation')
        self.assertEqual(test_practice.seats_used, 1, 'Practice: incorrect number of attendees after closing confirmation')
        test_reg2.action_set_done()
        self.assertEqual(test_reg1.state, 'done', 'Practice: wrong state of attended confirmation')
        self.assertEqual(test_practice.seats_used, 2, 'Practice: incorrect number of attendees after closing confirmation')

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_practice_flow(self):
        """ Advanced practice flow: no auto confirmation, manage minimum / maximum
        seats, ... """
        # PracticeUser creates a new practice: ok
        test_practice = self.env['practice.practice'].with_user(self.user_practicemanager).create({
            'name': 'TestPractice',
            'date_begin': datetime.datetime.now() + relativedelta(days=-1),
            'date_end': datetime.datetime.now() + relativedelta(days=1),
            'seats_limited': True,
            'seats_max': 10,
        })
        self.assertFalse(test_practice.auto_confirm)

        # PracticeUser create confirmations for this practice -> no auto confirmation
        test_reg1 = self.env['practice.confirmation'].with_user(self.user_practiceuser).create({
            'name': 'TestReg1',
            'practice_id': test_practice.id,
        })
        self.assertEqual(
            test_reg1.state, 'draft',
            'Practice: new confirmation should not be confirmed with auto_confirmation parameter being False')
