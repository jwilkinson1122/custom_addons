# -*- coding: utf-8 -*-


from datetime import date, datetime, timedelta
from unittest.mock import patch

from odoo import Command
from odoo.addons.prescription.tests.common import TestPrescriptionCommon
from odoo import exceptions
from odoo.fields import Datetime as FieldsDatetime, Date as FieldsDate
from odoo.tests.common import users, Form
from odoo.tools import mute_logger


class TestPrescriptionData(TestPrescriptionCommon):

    @classmethod
    def setUpClass(cls):
        super(TestPrescriptionData, cls).setUpClass()
        cls.patcher = patch('odoo.addons.prescription.models.prescription_prescription.fields.Datetime', wraps=FieldsDatetime)
        cls.mock_datetime = cls.patcher.start()
        cls.mock_datetime.now.return_value = datetime(2020, 1, 31, 10, 0, 0)
        cls.addClassCleanup(cls.patcher.stop)

        cls.prescription_0.write({
            'date_begin': datetime(2020, 2, 1, 8, 30, 0),
            'date_end': datetime(2020, 2, 4, 18, 45, 0),
        })

    @users('user_prescriptionmanager')
    def test_prescription_date_computation(self):
        prescription = self.prescription_0.with_user(self.env.user)
        prescription.write({
            'confirmation_ids': [(0, 0, {'partner_id': self.prescription_customer.id, 'name': 'test_reg'})],
            'date_begin': datetime(2020, 1, 31, 15, 0, 0),
            'date_end': datetime(2020, 4, 5, 18, 0, 0),
        })
        confirmation = prescription.confirmation_ids[0]
        self.assertEqual(confirmation.get_date_range_str(), u'today')

        prescription.date_begin = datetime(2020, 2, 1, 15, 0, 0)
        self.assertEqual(confirmation.get_date_range_str(), u'tomorrow')

        prescription.date_begin = datetime(2020, 2, 2, 6, 0, 0)
        self.assertEqual(confirmation.get_date_range_str(), u'in 2 days')

        prescription.date_begin = datetime(2020, 2, 20, 17, 0, 0)
        self.assertEqual(confirmation.get_date_range_str(), u'next month')

        prescription.date_begin = datetime(2020, 3, 1, 10, 0, 0)
        self.assertEqual(confirmation.get_date_range_str(), u'on Mar 1, 2020, 11:00:00 AM')

        # Is actually 8:30 to 20:00 in Mexico
        prescription.write({
            'date_begin': datetime(2020, 1, 31, 14, 30, 0),
            'date_end': datetime(2020, 2, 1, 2, 0, 0),
            'date_tz': 'Mexico/General'
        })
        self.assertTrue(prescription.is_one_day)

    @users('user_prescriptionmanager')
    def test_prescription_date_timezone(self):
        prescription = self.prescription_0.with_user(self.env.user)
        # Is actually 8:30 to 20:00 in Mexico
        prescription.write({
            'date_begin': datetime(2020, 1, 31, 14, 30, 0),
            'date_end': datetime(2020, 2, 1, 2, 0, 0),
            'date_tz': 'Mexico/General'
        })
        self.assertTrue(prescription.is_one_day)
        self.assertFalse(prescription.is_ongoing)

    @users('user_prescriptionmanager')
    @mute_logger('odoo.models.unlink')
    def test_prescription_configuration_from_type(self):
        """ Test data computation of prescription coming from its prescription.type template. """
        self.assertEqual(self.env.user.tz, 'Europe/Brussels')

        # ------------------------------------------------------------
        # STARTING DATA
        # ------------------------------------------------------------

        prescription_type = self.env['prescription.type'].browse(self.prescription_type_complex.id)

        prescription = self.env['prescription.prescription'].create({
            'name': 'Prescription Update Type',
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
            'prescription_mail_ids': False,
        })
        self.assertEqual(prescription.date_tz, self.env.user.tz)
        self.assertFalse(prescription.seats_limited)
        self.assertFalse(prescription.auto_confirm)
        self.assertEqual(prescription.prescription_mail_ids, self.env['prescription.mail'])
        self.assertEqual(prescription.prescription_device_ids, self.env['prescription.prescription.device'])

        confirmation = self._create_confirmations(prescription, 1)
        self.assertEqual(confirmation.state, 'draft')  # prescription is not auto confirm

        # ------------------------------------------------------------
        # FILL SYNC TEST
        # ------------------------------------------------------------

        # change template to a one with mails -> fill prescription as it is void
        prescription_type.write({
            'prescription_type_mail_ids': [(5, 0), (0, 0, {
                'interval_nbr': 1, 'interval_unit': 'days', 'interval_type': 'before_prescription',
                'template_ref': 'mail.template,%i' % self.env['ir.model.data']._xmlid_to_res_id('prescription.prescription_reminder')})
            ],
            'prescription_type_device_ids': [(5, 0), (0, 0, {'name': 'TestConfirmation'})],
        })
        prescription.write({'prescription_type_id': prescription_type.id})
        self.assertEqual(prescription.date_tz, 'Europe/Paris')
        self.assertTrue(prescription.seats_limited)
        self.assertEqual(prescription.seats_max, prescription_type.seats_max)
        self.assertTrue(prescription.auto_confirm)
        # check 2many fields being populated
        self.assertEqual(len(prescription.prescription_mail_ids), 1)
        self.assertEqual(prescription.prescription_mail_ids.interval_nbr, 1)
        self.assertEqual(prescription.prescription_mail_ids.interval_unit, 'days')
        self.assertEqual(prescription.prescription_mail_ids.interval_type, 'before_prescription')
        self.assertEqual(prescription.prescription_mail_ids.template_ref, self.env.ref('prescription.prescription_reminder'))
        self.assertEqual(len(prescription.prescription_device_ids), 1)

        # update template, unlink from prescription -> should not impact prescription
        prescription_type.write({'has_seats_limitation': False})
        self.assertEqual(prescription_type.seats_max, 0)
        self.assertTrue(prescription.seats_limited)
        self.assertEqual(prescription.seats_max, 30)  # original template value
        prescription.write({'prescription_type_id': False})
        self.assertEqual(prescription.prescription_type_id, self.env["prescription.type"])

        # set template back -> update prescription
        prescription.write({'prescription_type_id': prescription_type.id})
        self.assertFalse(prescription.seats_limited)
        self.assertEqual(prescription.seats_max, 0)
        self.assertEqual(len(prescription.prescription_device_ids), 1)
        prescription_device1 = prescription.prescription_device_ids[0]
        self.assertEqual(prescription_device1.name, 'TestConfirmation')

    @users('user_prescriptionmanager')
    def test_prescription_configuration_mails_from_type(self):
        """ Test data computation (related to mails) of prescription coming from its prescription.type template.
        This test uses pretty low level Form data checks, as manipulations in a non-saved Form are
        required to highlight an undesired behavior when switching prescription_type templates :
        prescription_mail_ids not linked to a confirmation were generated and kept when switching between
        different templates in the Form, which could rapidly lead to a substantial amount of
        undesired lines. """
        # setup test records
        prescription_type_default = self.env['prescription.type'].create({
            'name': 'Type Default',
            'auto_confirm': True,
            'prescription_type_mail_ids': False,
        })
        prescription_type_mails = self.env['prescription.type'].create({
            'name': 'Type Mails',
            'auto_confirm': False,
            'prescription_type_mail_ids': [
                Command.clear(),
                Command.create({
                    'notification_type': 'mail',
                    'interval_nbr': 77,
                    'interval_unit': 'days',
                    'interval_type': 'after_prescription',
                    'template_ref': 'mail.template,%i' % self.env['ir.model.data']._xmlid_to_res_id('prescription.prescription_reminder'),
                })
            ],
        })
        prescription = self.env['prescription.prescription'].create({
            'name': 'Prescription',
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
            'prescription_type_id': prescription_type_default.id
        })
        prescription.write({
            'prescription_mail_ids': [
                Command.clear(),
                Command.create({
                    'notification_type': 'mail',
                    'interval_unit': 'now',
                    'interval_type': 'after_sub',
                    'template_ref': 'mail.template,%i' % self.env['ir.model.data']._xmlid_to_res_id('prescription.prescription_subscription'),
                })
            ]
        })
        mail = prescription.prescription_mail_ids[0]
        confirmation = self._create_confirmations(prescription, 1)
        self.assertEqual(confirmation.state, 'open')  # prescription auto confirms
        # verify that mail is linked to the confirmation
        self.assertEqual(
            set(mail.mapped('mail_confirmation_ids.confirmation_id.id')),
            set([confirmation.id])
        )
        # start test scenario
        prescription_form = Form(prescription)
        # verify that mail is linked to the prescription in the form
        self.assertEqual(
            set(map(lambda m: m.get('id', None), prescription_form.prescription_mail_ids._records)),
            set([mail.id])
        )
        # switch to an prescription_type with a mail template which should be computed
        prescription_form.prescription_type_id = prescription_type_mails
        # verify that 2 mails were computed
        self.assertEqual(len(prescription_form.prescription_mail_ids._records), 2)
        # verify that the mail linked to the confirmation was kept
        self.assertTrue(filter(lambda m: m.get('id', None) == mail.id, prescription_form.prescription_mail_ids._records))
        # since the other computed prescription.mail is to be created from an prescription.type.mail template,
        # verify that its attributes are the correct ones
        computed_mail = next(filter(lambda m: m.get('id', None) != mail.id, prescription_form.prescription_mail_ids._records), {})
        self.assertEqual(computed_mail.get('interval_nbr', None), 77)
        self.assertEqual(computed_mail.get('interval_unit', None), 'days')
        self.assertEqual(computed_mail.get('interval_type', None), 'after_prescription')
        # switch back to an prescription type without a mail template
        prescription_form.prescription_type_id = prescription_type_default
        # verify that the mail linked to the confirmation was kept, and the other removed
        self.assertEqual(
            set(map(lambda m: m.get('id', None), prescription_form.prescription_mail_ids._records)),
            set([mail.id])
        )

    @users('user_prescriptionmanager')
    def test_prescription_configuration_note_from_type(self):
        prescription_type = self.env['prescription.type'].browse(self.prescription_type_complex.id)

        prescription = self.env['prescription.prescription'].create({
            'name': 'Prescription Update Type Note',
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
        })

        # verify that note is not propagated if the prescription type contains blank html
        prescription.write({'note': '<p>Prescription Note</p>'})
        prescription_type.write({'note': '<p><br></p>'})
        prescription.write({'prescription_type_id': prescription_type.id})
        self.assertEqual(prescription.note, '<p>Prescription Note</p>')

        # verify that note is correctly propagated if it contains non empty html
        prescription.write({'prescription_type_id': False})
        prescription_type.write({'note': '<p>Prescription Type Note</p>'})
        prescription.write({'prescription_type_id': prescription_type.id})
        self.assertEqual(prescription.note, '<p>Prescription Type Note</p>')

    @users('user_prescriptionmanager')
    def test_prescription_configuration_devices_from_type(self):
        """ Test data computation (related to devices) of prescription coming from its prescription.type template.
        This test uses pretty low level Form data checks, as manipulations in a non-saved Form are
        required to highlight an undesired behavior when switching prescription_type templates :
        prescription_device_ids not linked to a confirmation were generated and kept when switching between
        different templates in the Form, which could rapidly lead to a substantial amount of
        undesired lines. """
        # setup test records
        prescription_type_default = self.env['prescription.type'].create({
            'name': 'Type Default',
            'auto_confirm': True
        })
        prescription_type_devices = self.env['prescription.type'].create({
            'name': 'Type Devices',
            'auto_confirm': False
        })
        prescription_type_devices.write({
            'prescription_type_device_ids': [
                Command.clear(),
                Command.create({
                    'name': 'Default Device',
                    'seats_max': 10,
                })
            ]
        })
        prescription = self.env['prescription.prescription'].create({
            'name': 'Prescription',
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
            'prescription_type_id': prescription_type_default.id
        })
        prescription.write({
            'prescription_device_ids': [
                Command.clear(),
                Command.create({
                    'name': 'Confirmation Device',
                    'seats_max': 10,
                })
            ]
        })
        device = prescription.prescription_device_ids[0]
        confirmation = self._create_confirmations(prescription, 1)
        # link the device to the confirmation
        confirmation.write({'prescription_device_id': device.id})
        # start test scenario
        prescription_form = Form(prescription)
        # verify that the device is linked to the prescription in the form
        self.assertEqual(
            set(map(lambda m: m.get('name', None), prescription_form.prescription_device_ids._records)),
            set(['Confirmation Device'])
        )
        # switch to an prescription_type with a device template which should be computed
        prescription_form.prescription_type_id = prescription_type_devices
        # verify that both devices are computed
        self.assertEqual(
            set(map(lambda m: m.get('name', None), prescription_form.prescription_device_ids._records)),
            set(['Confirmation Device', 'Default Device'])
        )
        # switch back to an prescription_type without default devices
        prescription_form.prescription_type_id = prescription_type_default
        # verify that the device linked to the confirmation was kept, and the other removed
        self.assertEqual(
            set(map(lambda m: m.get('name', None), prescription_form.prescription_device_ids._records)),
            set(['Confirmation Device'])
        )

    @users('user_prescriptionmanager')
    def test_prescription_mail_default_config(self):
        prescription = self.env['prescription.prescription'].create({
            'name': 'Prescription Update Type',
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
        })
        self.assertEqual(prescription.date_tz, self.env.user.tz)
        self.assertFalse(prescription.seats_limited)
        self.assertFalse(prescription.auto_confirm)

        #Prescription Communications: when no prescription type, default configuration
        self.assertEqual(len(prescription.prescription_mail_ids), 3)
        self.assertEqual(prescription.prescription_mail_ids[0].interval_unit, 'now')
        self.assertEqual(prescription.prescription_mail_ids[0].interval_type, 'after_sub')
        self.assertEqual(prescription.prescription_mail_ids[0].template_ref, self.env.ref('prescription.prescription_subscription'))
        self.assertEqual(prescription.prescription_mail_ids[1].interval_nbr, 1)
        self.assertEqual(prescription.prescription_mail_ids[1].interval_unit, 'hours')
        self.assertEqual(prescription.prescription_mail_ids[1].interval_type, 'before_prescription')
        self.assertEqual(prescription.prescription_mail_ids[1].template_ref, self.env.ref('prescription.prescription_reminder'))
        self.assertEqual(prescription.prescription_mail_ids[2].interval_nbr, 3)
        self.assertEqual(prescription.prescription_mail_ids[2].interval_unit, 'days')
        self.assertEqual(prescription.prescription_mail_ids[2].interval_type, 'before_prescription')
        self.assertEqual(prescription.prescription_mail_ids[2].template_ref, self.env.ref('prescription.prescription_reminder'))

        prescription.write({
            'prescription_mail_ids': False
        })
        self.assertEqual(prescription.prescription_mail_ids, self.env['prescription.mail'])

    def test_prescription_mail_filter_template_on_prescription(self):
        """Test that the mail template are filtered to show only those which are related to the prescription confirmation model.

        This is important to be able to show only relevant mail templates on the related
        field "template_ref".
        """
        self.env['mail.template'].search([('model', '=', 'prescription.confirmation')]).unlink()
        self.env['mail.template'].create({'model_id': self.env['ir.model']._get('prescription.confirmation').id, 'name': 'test template'})
        self.env['mail.template'].create({'model_id': self.env['ir.model']._get('res.partner').id, 'name': 'test template'})
        templates = self.env['mail.template'].with_context(filter_template_on_prescription=True).name_search('test template')
        self.assertEqual(len(templates), 1, 'Should return only mail templates related to the prescription confirmation model')

    @users('user_prescriptionmanager')
    def test_prescription_registrable(self):
        """Test if `_compute_prescription_confirmations_open` works properly."""
        prescription = self.prescription_0.with_user(self.env.user)
        prescription.write({
            'date_begin': datetime(2020, 1, 30, 8, 0, 0),
            'date_end': datetime(2020, 1, 31, 8, 0, 0),
        })
        self.assertFalse(prescription.prescription_confirmations_open)
        prescription.write({
            'date_end': datetime(2020, 2, 4, 8, 0, 0),
        })
        self.assertTrue(prescription.prescription_confirmations_open)

        # device without dates boundaries -> ok
        device = self.env['prescription.prescription.device'].create({
            'name': 'TestDevice',
            'prescription_id': prescription.id,
        })
        self.assertTrue(prescription.prescription_confirmations_open)

        # even with valid devices, date limits confirmations
        prescription.write({
            'date_begin': datetime(2020, 1, 28, 15, 0, 0),
            'date_end': datetime(2020, 1, 30, 15, 0, 0),
        })
        self.assertFalse(prescription.prescription_confirmations_open)

        # no more seats available
        confirmation = self.env['prescription.confirmation'].create({
            'name': 'Albert Test',
            'prescription_id': prescription.id,
        })
        confirmation.action_confirm()
        prescription.write({
            'date_end': datetime(2020, 2, 1, 15, 0, 0),
            'seats_max': 1,
            'seats_limited': True,
        })
        self.assertEqual(prescription.seats_available, 0)
        self.assertFalse(prescription.prescription_confirmations_open)

        # seats available are back
        confirmation.unlink()
        self.assertEqual(prescription.seats_available, 1)
        self.assertTrue(prescription.prescription_confirmations_open)

        # but devices are expired
        device.write({'end_sale_datetime': datetime(2020, 1, 30, 15, 0, 0)})
        self.assertTrue(device.is_expired)
        self.assertFalse(prescription.prescription_confirmations_open)

    @users('user_prescriptionmanager')
    def test_prescription_ongoing(self):
        prescription_1 = self.env['prescription.prescription'].create({
            'name': 'Test Prescription 1',
            'date_begin': datetime(2020, 1, 25, 8, 0, 0),
            'date_end': datetime(2020, 2, 1, 18, 0, 0),
        })
        self.assertTrue(prescription_1.is_ongoing)
        ongoing_prescription_ids = self.env['prescription.prescription']._search([('is_ongoing', '=', True)])
        self.assertIn(prescription_1.id, ongoing_prescription_ids)

        prescription_1.update({'date_begin': datetime(2020, 2, 1, 9, 0, 0)})
        self.assertFalse(prescription_1.is_ongoing)
        ongoing_prescription_ids = self.env['prescription.prescription']._search([('is_ongoing', '=', True)])
        self.assertNotIn(prescription_1.id, ongoing_prescription_ids)

        prescription_2 = self.env['prescription.prescription'].create({
            'name': 'Test Prescription 2',
            'date_begin': datetime(2020, 1, 25, 8, 0, 0),
            'date_end': datetime(2020, 1, 28, 8, 0, 0),
        })
        self.assertFalse(prescription_2.is_ongoing)
        finished_or_upcoming_prescription_ids = self.env['prescription.prescription']._search([('is_ongoing', '=', False)])
        self.assertIn(prescription_2.id, finished_or_upcoming_prescription_ids)

        prescription_2.update({'date_end': datetime(2020, 2, 2, 8, 0, 1)})
        self.assertTrue(prescription_2.is_ongoing)
        finished_or_upcoming_prescription_ids = self.env['prescription.prescription']._search([('is_ongoing', '=', False)])
        self.assertNotIn(prescription_2.id, finished_or_upcoming_prescription_ids)

    @users('user_prescriptionmanager')
    def test_prescription_seats(self):
        prescription_type = self.prescription_type_complex.with_user(self.env.user)
        prescription = self.env['prescription.prescription'].create({
            'name': 'Prescription Update Type',
            'prescription_type_id': prescription_type.id,
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
        })

        self.assertEqual(prescription.address_id, self.env.user.company_id.partner_id)
        # seats: coming from prescription type configuration
        self.assertTrue(prescription.seats_limited)
        self.assertEqual(prescription.seats_available, prescription.prescription_type_id.seats_max)
        self.assertEqual(prescription.seats_unconfirmed, 0)
        self.assertEqual(prescription.seats_reserved, 0)
        self.assertEqual(prescription.seats_used, 0)
        self.assertEqual(prescription.seats_expected, 0)

        # create confirmation in order to check the seats computation
        self.assertTrue(prescription.auto_confirm)
        for x in range(5):
            reg = self.env['prescription.confirmation'].create({
                'prescription_id': prescription.id,
                'name': 'reg_open',
            })
            self.assertEqual(reg.state, 'open')
        reg_draft = self.env['prescription.confirmation'].create({
            'prescription_id': prescription.id,
            'name': 'reg_draft',
        })
        reg_draft.write({'state': 'draft'})
        reg_done = self.env['prescription.confirmation'].create({
            'prescription_id': prescription.id,
            'name': 'reg_done',
        })
        reg_done.write({'state': 'done'})
        self.assertEqual(prescription.seats_available, prescription.prescription_type_id.seats_max - 6)
        self.assertEqual(prescription.seats_unconfirmed, 1)
        self.assertEqual(prescription.seats_reserved, 5)
        self.assertEqual(prescription.seats_used, 1)
        self.assertEqual(prescription.seats_expected, 7)


class TestPrescriptionConfirmationData(TestPrescriptionCommon):

    @users('user_prescriptionmanager')
    def test_confirmation_partner_sync(self):
        """ Test confirmation computed fields about partner """
        test_email = '"Nibbler In Space" <nibbler@futurama.example.com>'
        test_phone = '0456001122'

        prescription = self.env['prescription.prescription'].browse(self.prescription_0.ids)
        customer = self.env['res.partner'].browse(self.prescription_customer.id)

        # take all from partner
        prescription.write({
            'confirmation_ids': [(0, 0, {
                'partner_id': customer.id,
            })]
        })
        new_reg = prescription.confirmation_ids[0]
        self.assertEqual(new_reg.partner_id, customer)
        self.assertEqual(new_reg.name, customer.name)
        self.assertEqual(new_reg.email, customer.email)
        self.assertEqual(new_reg.phone, customer.phone)

        # partial update
        prescription.write({
            'confirmation_ids': [(0, 0, {
                'partner_id': customer.id,
                'name': 'Nibbler In Space',
                'email': test_email,
            })]
        })
        new_reg = prescription.confirmation_ids.sorted()[0]
        self.assertEqual(new_reg.partner_id, customer)
        self.assertEqual(
            new_reg.name, 'Nibbler In Space',
            'Confirmation should take user input over computed partner value')
        self.assertEqual(
            new_reg.email, test_email,
            'Confirmation should take user input over computed partner value')
        self.assertEqual(
            new_reg.phone, customer.phone,
            'Confirmation should take partner value if not user input')

        # already filled information should not be updated
        prescription.write({
            'confirmation_ids': [(0, 0, {
                'name': 'Nibbler In Space',
                'phone': test_phone,
            })]
        })
        new_reg = prescription.confirmation_ids.sorted()[0]
        self.assertEqual(new_reg.name, 'Nibbler In Space')
        self.assertEqual(new_reg.email, False)
        self.assertEqual(new_reg.phone, test_phone)
        new_reg.write({'partner_id': customer.id})
        self.assertEqual(new_reg.partner_id, customer)
        self.assertEqual(new_reg.name, 'Nibbler In Space')
        self.assertEqual(new_reg.email, customer.email)
        self.assertEqual(new_reg.phone, test_phone)

    @users('user_prescriptionmanager')
    def test_confirmation_partner_sync_company(self):
        """ Test synchronization involving companies """
        prescription = self.env['prescription.prescription'].browse(self.prescription_0.ids)
        customer = self.env['res.partner'].browse(self.prescription_customer.id)

        # create company structure (using sudo as required partner manager group)
        company = self.env['res.partner'].sudo().create({
            'name': 'Customer Company',
            'is_company': True,
            'type': 'other',
        })
        customer.sudo().write({'type': 'invoice', 'parent_id': company.id})
        contact = self.env['res.partner'].sudo().create({
            'name': 'ContactName',
            'parent_id': company.id,
            'type': 'contact',
            'email': 'ContactEmail <contact.email@test.example.com>',
            'phone': '+32456998877',
        })

        # take all from partner
        prescription.write({
            'confirmation_ids': [(0, 0, {
                'partner_id': customer.id,
            })]
        })
        new_reg = prescription.confirmation_ids[0]
        self.assertEqual(new_reg.partner_id, customer)
        self.assertEqual(new_reg.name, contact.name)
        self.assertEqual(new_reg.email, contact.email)
        self.assertEqual(new_reg.phone, contact.phone)


class TestPrescriptionDeviceData(TestPrescriptionCommon):

    def setUp(self):
        super(TestPrescriptionDeviceData, self).setUp()
        self.device_date_patcher = patch('odoo.addons.prescription.models.prescription_device.fields.Date', wraps=FieldsDate)
        self.device_date_patcher_mock = self.device_date_patcher.start()
        self.device_date_patcher_mock.context_today.return_value = date(2020, 1, 31)
        self.device_datetime_patcher = patch('odoo.addons.prescription.models.prescription_device.fields.Datetime', wraps=FieldsDatetime)
        self.device_datetime_patcher_mock = self.device_datetime_patcher.start()
        self.device_datetime_patcher_mock.now.return_value = datetime(2020, 1, 31, 10, 0, 0)

    def tearDown(self):
        super(TestPrescriptionDeviceData, self).tearDown()
        self.device_date_patcher.stop()
        self.device_datetime_patcher.stop()

    @users('user_prescriptionmanager')
    def test_prescription_device_fields(self):
        """ Test prescription device fields synchronization """
        prescription = self.prescription_0.with_user(self.env.user)
        prescription.write({
            'prescription_device_ids': [
                (5, 0),
                (0, 0, {
                    'name': 'First Device',
                    'seats_max': 30,
                }), (0, 0, {  # limited in time, available (01/10 (start) < 01/31 (today) < 02/10 (end))
                    'name': 'Second Device',
                    'start_sale_datetime': datetime(2020, 1, 10, 0, 0, 0),
                    'end_sale_datetime': datetime(2020, 2, 10, 23, 59, 59),
                })
            ],
        })
        first_device = prescription.prescription_device_ids.filtered(lambda t: t.name == 'First Device')
        second_device = prescription.prescription_device_ids.filtered(lambda t: t.name == 'Second Device')

        self.assertTrue(first_device.seats_limited)
        self.assertTrue(first_device.sale_available)
        self.assertFalse(first_device.is_expired)

        self.assertFalse(second_device.seats_limited)
        self.assertTrue(second_device.sale_available)
        self.assertFalse(second_device.is_expired)
        # sale is ended
        second_device.write({'end_sale_datetime': datetime(2020, 1, 20, 23, 59, 59)})
        self.assertFalse(second_device.sale_available)
        self.assertTrue(second_device.is_expired)
        # sale has not started
        second_device.write({
            'start_sale_datetime': datetime(2020, 2, 10, 0, 0, 0),
            'end_sale_datetime': datetime(2020, 2, 20, 23, 59, 59),
        })
        self.assertFalse(second_device.sale_available)
        self.assertFalse(second_device.is_expired)
        # sale started today
        second_device.write({
            'start_sale_datetime': datetime(2020, 1, 31, 0, 0, 0),
            'end_sale_datetime': datetime(2020, 2, 20, 23, 59, 59),
        })
        self.assertTrue(second_device.sale_available)
        self.assertTrue(second_device.is_launched())
        self.assertFalse(second_device.is_expired)
        # incoherent dates are invalid
        with self.assertRaises(exceptions.UserError):
            second_device.write({'end_sale_datetime': datetime(2020, 1, 20, 23, 59, 59)})

        #test if prescription start/end dates are taking datetime fields (hours, minutes, seconds) into account
        second_device.write({'start_sale_datetime': datetime(2020, 1, 31, 11, 0, 0)})
        self.assertFalse(second_device.sale_available)
        self.assertFalse(second_device.is_launched())

        second_device.write({
            'start_sale_datetime': datetime(2020, 1, 31, 7, 0, 0),
            'end_sale_datetime': datetime(2020, 2, 27, 13, 0, 0)
        })

        self.assertTrue(second_device.sale_available)
        self.assertTrue(second_device.is_launched())
        self.assertFalse(second_device.is_expired)

        second_device.write({
            'end_sale_datetime': datetime(2020, 1, 31, 9, 0, 0)
        })

        self.assertFalse(second_device.sale_available)
        self.assertTrue(second_device.is_expired)


class TestPrescriptionTypeData(TestPrescriptionCommon):

    @users('user_prescriptionmanager')
    def test_prescription_type_fields(self):
        """ Test prescription type fields synchronization """
        # create test type and ensure its initial values
        prescription_type = self.env['prescription.type'].create({
            'name': 'Testing fields computation',
            'has_seats_limitation': True,
            'seats_max': 30,
        })
        self.assertTrue(prescription_type.has_seats_limitation)
        self.assertEqual(prescription_type.seats_max, 30)

        # reset seats limitation
        prescription_type.write({'has_seats_limitation': False})
        self.assertFalse(prescription_type.has_seats_limitation)
        self.assertEqual(prescription_type.seats_max, 0)
