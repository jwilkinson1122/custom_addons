# -*- coding: utf-8 -*-


import datetime

from dateutil.relativedelta import relativedelta

from odoo.addons.prescription.tests.common import TestPrescriptionCommon
from odoo.exceptions import ValidationError
from odoo.tests.common import Form
from odoo.tools import mute_logger


class TestPrescriptionUI(TestPrescriptionCommon):

    def test_prescription_confirmation_partner_sync(self):
        """ Ensure onchange on partner_id is kept for interface, not for computed
        fields. """
        confirmation_form = Form(self.env['prescription.confirmation'].with_context(
            default_name='WrongName',
            default_prescription_id=self.prescription_0.id
        ))
        self.assertEqual(confirmation_form.prescription_id, self.prescription_0)
        self.assertEqual(confirmation_form.name, 'WrongName')
        self.assertFalse(confirmation_form.email)
        self.assertFalse(confirmation_form.phone)
        self.assertFalse(confirmation_form.mobile)

        # trigger onchange
        confirmation_form.partner_id = self.prescription_customer
        self.assertEqual(confirmation_form.name, self.prescription_customer.name)
        self.assertEqual(confirmation_form.email, self.prescription_customer.email)
        self.assertEqual(confirmation_form.phone, self.prescription_customer.phone)
        self.assertEqual(confirmation_form.mobile, self.prescription_customer.mobile)

        # save, check record matches Form values
        confirmation = confirmation_form.save()
        self.assertEqual(confirmation.partner_id, self.prescription_customer)
        self.assertEqual(confirmation.name, self.prescription_customer.name)
        self.assertEqual(confirmation.email, self.prescription_customer.email)
        self.assertEqual(confirmation.phone, self.prescription_customer.phone)
        self.assertEqual(confirmation.mobile, self.prescription_customer.mobile)

        # allow writing on some fields independently from customer config
        confirmation.write({'phone': False, 'mobile': False})
        self.assertFalse(confirmation.phone)
        self.assertFalse(confirmation.mobile)

        # reset partner should not reset other fields
        confirmation.write({'partner_id': False})
        self.assertEqual(confirmation.partner_id, self.env['res.partner'])
        self.assertEqual(confirmation.name, self.prescription_customer.name)
        self.assertEqual(confirmation.email, self.prescription_customer.email)
        self.assertFalse(confirmation.phone)
        self.assertFalse(confirmation.mobile)

        # update to a new partner not through UI -> update only void feilds
        confirmation.write({'partner_id': self.prescription_customer2.id})
        self.assertEqual(confirmation.partner_id, self.prescription_customer2)
        self.assertEqual(confirmation.name, self.prescription_customer.name)
        self.assertEqual(confirmation.email, self.prescription_customer.email)
        self.assertEqual(confirmation.phone, self.prescription_customer2.phone)
        self.assertEqual(confirmation.mobile, self.prescription_customer2.mobile)


class TestPrescriptionFlow(TestPrescriptionCommon):

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_prescription_auto_confirm(self):
        """ Basic prescription management with auto confirmation """
        # PrescriptionUser creates a new prescription: ok
        test_prescription = self.env['prescription.prescription'].with_user(self.user_prescriptionmanager).create({
            'name': 'TestPrescription',
            'auto_confirm': True,
            'date_begin': datetime.datetime.now() + relativedelta(days=-1),
            'date_end': datetime.datetime.now() + relativedelta(days=1),
            'seats_max': 2,
            'seats_limited': True,
        })
        self.assertTrue(test_prescription.auto_confirm)

        # PrescriptionUser create confirmations for this prescription
        test_reg1 = self.env['prescription.confirmation'].with_user(self.user_prescriptionuser).create({
            'name': 'TestReg1',
            'prescription_id': test_prescription.id,
        })
        self.assertEqual(test_reg1.state, 'open', 'Prescription: auto_confirmation of confirmation failed')
        self.assertEqual(test_prescription.seats_reserved, 1, 'Prescription: wrong number of reserved seats after confirmed confirmation')
        test_reg2 = self.env['prescription.confirmation'].with_user(self.user_prescriptionuser).create({
            'name': 'TestReg2',
            'prescription_id': test_prescription.id,
        })
        self.assertEqual(test_reg2.state, 'open', 'Prescription: auto_confirmation of confirmation failed')
        self.assertEqual(test_prescription.seats_reserved, 2, 'Prescription: wrong number of reserved seats after confirmed confirmation')

        # PrescriptionUser create confirmations for this prescription: too much confirmations
        with self.assertRaises(ValidationError):
            self.env['prescription.confirmation'].with_user(self.user_prescriptionuser).create({
                'name': 'TestReg3',
                'prescription_id': test_prescription.id,
            })

        # PrescriptionUser validates confirmations
        test_reg1.action_set_done()
        self.assertEqual(test_reg1.state, 'done', 'Prescription: wrong state of attended confirmation')
        self.assertEqual(test_prescription.seats_used, 1, 'Prescription: incorrect number of attendees after closing confirmation')
        test_reg2.action_set_done()
        self.assertEqual(test_reg1.state, 'done', 'Prescription: wrong state of attended confirmation')
        self.assertEqual(test_prescription.seats_used, 2, 'Prescription: incorrect number of attendees after closing confirmation')

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_prescription_flow(self):
        """ Advanced prescription flow: no auto confirmation, manage minimum / maximum
        seats, ... """
        # PrescriptionUser creates a new prescription: ok
        test_prescription = self.env['prescription.prescription'].with_user(self.user_prescriptionmanager).create({
            'name': 'TestPrescription',
            'date_begin': datetime.datetime.now() + relativedelta(days=-1),
            'date_end': datetime.datetime.now() + relativedelta(days=1),
            'seats_limited': True,
            'seats_max': 10,
        })
        self.assertFalse(test_prescription.auto_confirm)

        # PrescriptionUser create confirmations for this prescription -> no auto confirmation
        test_reg1 = self.env['prescription.confirmation'].with_user(self.user_prescriptionuser).create({
            'name': 'TestReg1',
            'prescription_id': test_prescription.id,
        })
        self.assertEqual(
            test_reg1.state, 'draft',
            'Prescription: new confirmation should not be confirmed with auto_confirmation parameter being False')
