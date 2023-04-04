# -*- coding: utf-8 -*-


import datetime

from dateutil.relativedelta import relativedelta

from odoo.addons.prescription.tests.common import TestPrescriptionCommon
from odoo.exceptions import ValidationError
from odoo.tests.common import Form
from odoo.tools import mute_logger


class TestPrescriptionUI(TestPrescriptionCommon):

    def test_prescription_registration_partner_sync(self):
        """ Ensure onchange on partner_id is kept for interface, not for computed
        fields. """
        registration_form = Form(self.env['prescription.registration'].with_context(
            default_name='WrongName',
            default_prescription_id=self.prescription_0.id
        ))
        self.assertEqual(registration_form.prescription_id, self.prescription_0)
        self.assertEqual(registration_form.name, 'WrongName')
        self.assertFalse(registration_form.email)
        self.assertFalse(registration_form.phone)
        self.assertFalse(registration_form.mobile)

        # trigger onchange
        registration_form.partner_id = self.prescription_customer
        self.assertEqual(registration_form.name, self.prescription_customer.name)
        self.assertEqual(registration_form.email, self.prescription_customer.email)
        self.assertEqual(registration_form.phone, self.prescription_customer.phone)
        self.assertEqual(registration_form.mobile, self.prescription_customer.mobile)

        # save, check record matches Form values
        registration = registration_form.save()
        self.assertEqual(registration.partner_id, self.prescription_customer)
        self.assertEqual(registration.name, self.prescription_customer.name)
        self.assertEqual(registration.email, self.prescription_customer.email)
        self.assertEqual(registration.phone, self.prescription_customer.phone)
        self.assertEqual(registration.mobile, self.prescription_customer.mobile)

        # allow writing on some fields independently from customer config
        registration.write({'phone': False, 'mobile': False})
        self.assertFalse(registration.phone)
        self.assertFalse(registration.mobile)

        # reset partner should not reset other fields
        registration.write({'partner_id': False})
        self.assertEqual(registration.partner_id, self.env['res.partner'])
        self.assertEqual(registration.name, self.prescription_customer.name)
        self.assertEqual(registration.email, self.prescription_customer.email)
        self.assertFalse(registration.phone)
        self.assertFalse(registration.mobile)

        # update to a new partner not through UI -> update only void feilds
        registration.write({'partner_id': self.prescription_customer2.id})
        self.assertEqual(registration.partner_id, self.prescription_customer2)
        self.assertEqual(registration.name, self.prescription_customer.name)
        self.assertEqual(registration.email, self.prescription_customer.email)
        self.assertEqual(registration.phone, self.prescription_customer2.phone)
        self.assertEqual(registration.mobile, self.prescription_customer2.mobile)


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

        # PrescriptionUser create registrations for this prescription
        test_reg1 = self.env['prescription.registration'].with_user(self.user_prescriptionuser).create({
            'name': 'TestReg1',
            'prescription_id': test_prescription.id,
        })
        self.assertEqual(test_reg1.state, 'open', 'Prescription: auto_confirmation of registration failed')
        self.assertEqual(test_prescription.seats_reserved, 1, 'Prescription: wrong number of reserved seats after confirmed registration')
        test_reg2 = self.env['prescription.registration'].with_user(self.user_prescriptionuser).create({
            'name': 'TestReg2',
            'prescription_id': test_prescription.id,
        })
        self.assertEqual(test_reg2.state, 'open', 'Prescription: auto_confirmation of registration failed')
        self.assertEqual(test_prescription.seats_reserved, 2, 'Prescription: wrong number of reserved seats after confirmed registration')

        # PrescriptionUser create registrations for this prescription: too much registrations
        with self.assertRaises(ValidationError):
            self.env['prescription.registration'].with_user(self.user_prescriptionuser).create({
                'name': 'TestReg3',
                'prescription_id': test_prescription.id,
            })

        # PrescriptionUser validates registrations
        test_reg1.action_set_done()
        self.assertEqual(test_reg1.state, 'done', 'Prescription: wrong state of attended registration')
        self.assertEqual(test_prescription.seats_used, 1, 'Prescription: incorrect number of attendees after closing registration')
        test_reg2.action_set_done()
        self.assertEqual(test_reg1.state, 'done', 'Prescription: wrong state of attended registration')
        self.assertEqual(test_prescription.seats_used, 2, 'Prescription: incorrect number of attendees after closing registration')

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

        # PrescriptionUser create registrations for this prescription -> no auto confirmation
        test_reg1 = self.env['prescription.registration'].with_user(self.user_prescriptionuser).create({
            'name': 'TestReg1',
            'prescription_id': test_prescription.id,
        })
        self.assertEqual(
            test_reg1.state, 'draft',
            'Prescription: new registration should not be confirmed with auto_confirmation parameter being False')
