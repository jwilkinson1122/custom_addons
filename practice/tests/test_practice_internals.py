# -*- coding: utf-8 -*-


from datetime import date, datetime, timedelta
from unittest.mock import patch

from odoo import Command
from odoo.addons.practice.tests.common import TestPracticeCommon
from odoo import exceptions
from odoo.fields import Datetime as FieldsDatetime, Date as FieldsDate
from odoo.tests.common import users, Form
from odoo.tools import mute_logger


class TestPracticeData(TestPracticeCommon):

    @classmethod
    def setUpClass(cls):
        super(TestPracticeData, cls).setUpClass()
        cls.patcher = patch('odoo.addons.practice.models.practice_practice.fields.Datetime', wraps=FieldsDatetime)
        cls.mock_datetime = cls.patcher.start()
        cls.mock_datetime.now.return_value = datetime(2020, 1, 31, 10, 0, 0)
        cls.addClassCleanup(cls.patcher.stop)

        cls.practice_0.write({
            'date_begin': datetime(2020, 2, 1, 8, 30, 0),
            'date_end': datetime(2020, 2, 4, 18, 45, 0),
        })

    @users('user_practicemanager')
    def test_practice_date_computation(self):
        practice = self.practice_0.with_user(self.env.user)
        practice.write({
            'confirmation_ids': [(0, 0, {'partner_id': self.practice_customer.id, 'name': 'test_reg'})],
            'date_begin': datetime(2020, 1, 31, 15, 0, 0),
            'date_end': datetime(2020, 4, 5, 18, 0, 0),
        })
        confirmation = practice.confirmation_ids[0]
        self.assertEqual(confirmation.get_date_range_str(), u'today')

        practice.date_begin = datetime(2020, 2, 1, 15, 0, 0)
        self.assertEqual(confirmation.get_date_range_str(), u'tomorrow')

        practice.date_begin = datetime(2020, 2, 2, 6, 0, 0)
        self.assertEqual(confirmation.get_date_range_str(), u'in 2 days')

        practice.date_begin = datetime(2020, 2, 20, 17, 0, 0)
        self.assertEqual(confirmation.get_date_range_str(), u'next month')

        practice.date_begin = datetime(2020, 3, 1, 10, 0, 0)
        self.assertEqual(confirmation.get_date_range_str(), u'on Mar 1, 2020, 11:00:00 AM')

        # Is actually 8:30 to 20:00 in Mexico
        practice.write({
            'date_begin': datetime(2020, 1, 31, 14, 30, 0),
            'date_end': datetime(2020, 2, 1, 2, 0, 0),
            'date_tz': 'Mexico/General'
        })
        self.assertTrue(practice.is_one_day)

    @users('user_practicemanager')
    def test_practice_date_timezone(self):
        practice = self.practice_0.with_user(self.env.user)
        # Is actually 8:30 to 20:00 in Mexico
        practice.write({
            'date_begin': datetime(2020, 1, 31, 14, 30, 0),
            'date_end': datetime(2020, 2, 1, 2, 0, 0),
            'date_tz': 'Mexico/General'
        })
        self.assertTrue(practice.is_one_day)
        self.assertFalse(practice.is_ongoing)

    @users('user_practicemanager')
    @mute_logger('odoo.models.unlink')
    def test_practice_configuration_from_type(self):
        """ Test data computation of practice coming from its practice.type template. """
        self.assertEqual(self.env.user.tz, 'Europe/Brussels')

        # ------------------------------------------------------------
        # STARTING DATA
        # ------------------------------------------------------------

        practice_type = self.env['practice.type'].browse(self.practice_type_complex.id)

        practice = self.env['practice.practice'].create({
            'name': 'Practice Update Type',
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
            'practice_mail_ids': False,
        })
        self.assertEqual(practice.date_tz, self.env.user.tz)
        self.assertFalse(practice.seats_limited)
        self.assertFalse(practice.auto_confirm)
        self.assertEqual(practice.practice_mail_ids, self.env['practice.mail'])
        self.assertEqual(practice.practice_device_ids, self.env['practice.practice.device'])

        confirmation = self._create_confirmations(practice, 1)
        self.assertEqual(confirmation.state, 'draft')  # practice is not auto confirm

        # ------------------------------------------------------------
        # FILL SYNC TEST
        # ------------------------------------------------------------

        # change template to a one with mails -> fill practice as it is void
        practice_type.write({
            'practice_type_mail_ids': [(5, 0), (0, 0, {
                'interval_nbr': 1, 'interval_unit': 'days', 'interval_type': 'before_practice',
                'template_ref': 'mail.template,%i' % self.env['ir.model.data']._xmlid_to_res_id('practice.practice_reminder')})
            ],
            'practice_type_device_ids': [(5, 0), (0, 0, {'name': 'TestConfirmation'})],
        })
        practice.write({'practice_type_id': practice_type.id})
        self.assertEqual(practice.date_tz, 'Europe/Paris')
        self.assertTrue(practice.seats_limited)
        self.assertEqual(practice.seats_max, practice_type.seats_max)
        self.assertTrue(practice.auto_confirm)
        # check 2many fields being populated
        self.assertEqual(len(practice.practice_mail_ids), 1)
        self.assertEqual(practice.practice_mail_ids.interval_nbr, 1)
        self.assertEqual(practice.practice_mail_ids.interval_unit, 'days')
        self.assertEqual(practice.practice_mail_ids.interval_type, 'before_practice')
        self.assertEqual(practice.practice_mail_ids.template_ref, self.env.ref('practice.practice_reminder'))
        self.assertEqual(len(practice.practice_device_ids), 1)

        # update template, unlink from practice -> should not impact practice
        practice_type.write({'has_seats_limitation': False})
        self.assertEqual(practice_type.seats_max, 0)
        self.assertTrue(practice.seats_limited)
        self.assertEqual(practice.seats_max, 30)  # original template value
        practice.write({'practice_type_id': False})
        self.assertEqual(practice.practice_type_id, self.env["practice.type"])

        # set template back -> update practice
        practice.write({'practice_type_id': practice_type.id})
        self.assertFalse(practice.seats_limited)
        self.assertEqual(practice.seats_max, 0)
        self.assertEqual(len(practice.practice_device_ids), 1)
        practice_device1 = practice.practice_device_ids[0]
        self.assertEqual(practice_device1.name, 'TestConfirmation')

    @users('user_practicemanager')
    def test_practice_configuration_mails_from_type(self):
        """ Test data computation (related to mails) of practice coming from its practice.type template.
        This test uses pretty low level Form data checks, as manipulations in a non-saved Form are
        required to highlight an undesired behavior when switching practice_type templates :
        practice_mail_ids not linked to a confirmation were generated and kept when switching between
        different templates in the Form, which could rapidly lead to a substantial amount of
        undesired lines. """
        # setup test records
        practice_type_default = self.env['practice.type'].create({
            'name': 'Type Default',
            'auto_confirm': True,
            'practice_type_mail_ids': False,
        })
        practice_type_mails = self.env['practice.type'].create({
            'name': 'Type Mails',
            'auto_confirm': False,
            'practice_type_mail_ids': [
                Command.clear(),
                Command.create({
                    'notification_type': 'mail',
                    'interval_nbr': 77,
                    'interval_unit': 'days',
                    'interval_type': 'after_practice',
                    'template_ref': 'mail.template,%i' % self.env['ir.model.data']._xmlid_to_res_id('practice.practice_reminder'),
                })
            ],
        })
        practice = self.env['practice.practice'].create({
            'name': 'Practice',
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
            'practice_type_id': practice_type_default.id
        })
        practice.write({
            'practice_mail_ids': [
                Command.clear(),
                Command.create({
                    'notification_type': 'mail',
                    'interval_unit': 'now',
                    'interval_type': 'after_sub',
                    'template_ref': 'mail.template,%i' % self.env['ir.model.data']._xmlid_to_res_id('practice.practice_subscription'),
                })
            ]
        })
        mail = practice.practice_mail_ids[0]
        confirmation = self._create_confirmations(practice, 1)
        self.assertEqual(confirmation.state, 'open')  # practice auto confirms
        # verify that mail is linked to the confirmation
        self.assertEqual(
            set(mail.mapped('mail_confirmation_ids.confirmation_id.id')),
            set([confirmation.id])
        )
        # start test scenario
        practice_form = Form(practice)
        # verify that mail is linked to the practice in the form
        self.assertEqual(
            set(map(lambda m: m.get('id', None), practice_form.practice_mail_ids._records)),
            set([mail.id])
        )
        # switch to an practice_type with a mail template which should be computed
        practice_form.practice_type_id = practice_type_mails
        # verify that 2 mails were computed
        self.assertEqual(len(practice_form.practice_mail_ids._records), 2)
        # verify that the mail linked to the confirmation was kept
        self.assertTrue(filter(lambda m: m.get('id', None) == mail.id, practice_form.practice_mail_ids._records))
        # since the other computed practice.mail is to be created from an practice.type.mail template,
        # verify that its attributes are the correct ones
        computed_mail = next(filter(lambda m: m.get('id', None) != mail.id, practice_form.practice_mail_ids._records), {})
        self.assertEqual(computed_mail.get('interval_nbr', None), 77)
        self.assertEqual(computed_mail.get('interval_unit', None), 'days')
        self.assertEqual(computed_mail.get('interval_type', None), 'after_practice')
        # switch back to an practice type without a mail template
        practice_form.practice_type_id = practice_type_default
        # verify that the mail linked to the confirmation was kept, and the other removed
        self.assertEqual(
            set(map(lambda m: m.get('id', None), practice_form.practice_mail_ids._records)),
            set([mail.id])
        )

    @users('user_practicemanager')
    def test_practice_configuration_note_from_type(self):
        practice_type = self.env['practice.type'].browse(self.practice_type_complex.id)

        practice = self.env['practice.practice'].create({
            'name': 'Practice Update Type Note',
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
        })

        # verify that note is not propagated if the practice type contains blank html
        practice.write({'note': '<p>Practice Note</p>'})
        practice_type.write({'note': '<p><br></p>'})
        practice.write({'practice_type_id': practice_type.id})
        self.assertEqual(practice.note, '<p>Practice Note</p>')

        # verify that note is correctly propagated if it contains non empty html
        practice.write({'practice_type_id': False})
        practice_type.write({'note': '<p>Practice Type Note</p>'})
        practice.write({'practice_type_id': practice_type.id})
        self.assertEqual(practice.note, '<p>Practice Type Note</p>')

    @users('user_practicemanager')
    def test_practice_configuration_devices_from_type(self):
        """ Test data computation (related to devices) of practice coming from its practice.type template.
        This test uses pretty low level Form data checks, as manipulations in a non-saved Form are
        required to highlight an undesired behavior when switching practice_type templates :
        practice_device_ids not linked to a confirmation were generated and kept when switching between
        different templates in the Form, which could rapidly lead to a substantial amount of
        undesired lines. """
        # setup test records
        practice_type_default = self.env['practice.type'].create({
            'name': 'Type Default',
            'auto_confirm': True
        })
        practice_type_devices = self.env['practice.type'].create({
            'name': 'Type Devices',
            'auto_confirm': False
        })
        practice_type_devices.write({
            'practice_type_device_ids': [
                Command.clear(),
                Command.create({
                    'name': 'Default Device',
                    'seats_max': 10,
                })
            ]
        })
        practice = self.env['practice.practice'].create({
            'name': 'Practice',
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
            'practice_type_id': practice_type_default.id
        })
        practice.write({
            'practice_device_ids': [
                Command.clear(),
                Command.create({
                    'name': 'Confirmation Device',
                    'seats_max': 10,
                })
            ]
        })
        device = practice.practice_device_ids[0]
        confirmation = self._create_confirmations(practice, 1)
        # link the device to the confirmation
        confirmation.write({'practice_device_id': device.id})
        # start test scenario
        practice_form = Form(practice)
        # verify that the device is linked to the practice in the form
        self.assertEqual(
            set(map(lambda m: m.get('name', None), practice_form.practice_device_ids._records)),
            set(['Confirmation Device'])
        )
        # switch to an practice_type with a device template which should be computed
        practice_form.practice_type_id = practice_type_devices
        # verify that both devices are computed
        self.assertEqual(
            set(map(lambda m: m.get('name', None), practice_form.practice_device_ids._records)),
            set(['Confirmation Device', 'Default Device'])
        )
        # switch back to an practice_type without default devices
        practice_form.practice_type_id = practice_type_default
        # verify that the device linked to the confirmation was kept, and the other removed
        self.assertEqual(
            set(map(lambda m: m.get('name', None), practice_form.practice_device_ids._records)),
            set(['Confirmation Device'])
        )

    @users('user_practicemanager')
    def test_practice_mail_default_config(self):
        practice = self.env['practice.practice'].create({
            'name': 'Practice Update Type',
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
        })
        self.assertEqual(practice.date_tz, self.env.user.tz)
        self.assertFalse(practice.seats_limited)
        self.assertFalse(practice.auto_confirm)

        #Practice Communications: when no practice type, default configuration
        self.assertEqual(len(practice.practice_mail_ids), 3)
        self.assertEqual(practice.practice_mail_ids[0].interval_unit, 'now')
        self.assertEqual(practice.practice_mail_ids[0].interval_type, 'after_sub')
        self.assertEqual(practice.practice_mail_ids[0].template_ref, self.env.ref('practice.practice_subscription'))
        self.assertEqual(practice.practice_mail_ids[1].interval_nbr, 1)
        self.assertEqual(practice.practice_mail_ids[1].interval_unit, 'hours')
        self.assertEqual(practice.practice_mail_ids[1].interval_type, 'before_practice')
        self.assertEqual(practice.practice_mail_ids[1].template_ref, self.env.ref('practice.practice_reminder'))
        self.assertEqual(practice.practice_mail_ids[2].interval_nbr, 3)
        self.assertEqual(practice.practice_mail_ids[2].interval_unit, 'days')
        self.assertEqual(practice.practice_mail_ids[2].interval_type, 'before_practice')
        self.assertEqual(practice.practice_mail_ids[2].template_ref, self.env.ref('practice.practice_reminder'))

        practice.write({
            'practice_mail_ids': False
        })
        self.assertEqual(practice.practice_mail_ids, self.env['practice.mail'])

    def test_practice_mail_filter_template_on_practice(self):
        """Test that the mail template are filtered to show only those which are related to the practice confirmation model.

        This is important to be able to show only relevant mail templates on the related
        field "template_ref".
        """
        self.env['mail.template'].search([('model', '=', 'practice.confirmation')]).unlink()
        self.env['mail.template'].create({'model_id': self.env['ir.model']._get('practice.confirmation').id, 'name': 'test template'})
        self.env['mail.template'].create({'model_id': self.env['ir.model']._get('res.partner').id, 'name': 'test template'})
        templates = self.env['mail.template'].with_context(filter_template_on_practice=True).name_search('test template')
        self.assertEqual(len(templates), 1, 'Should return only mail templates related to the practice confirmation model')

    @users('user_practicemanager')
    def test_practice_registrable(self):
        """Test if `_compute_practice_confirmations_open` works properly."""
        practice = self.practice_0.with_user(self.env.user)
        practice.write({
            'date_begin': datetime(2020, 1, 30, 8, 0, 0),
            'date_end': datetime(2020, 1, 31, 8, 0, 0),
        })
        self.assertFalse(practice.practice_confirmations_open)
        practice.write({
            'date_end': datetime(2020, 2, 4, 8, 0, 0),
        })
        self.assertTrue(practice.practice_confirmations_open)

        # device without dates boundaries -> ok
        device = self.env['practice.practice.device'].create({
            'name': 'TestDevice',
            'practice_id': practice.id,
        })
        self.assertTrue(practice.practice_confirmations_open)

        # even with valid devices, date limits confirmations
        practice.write({
            'date_begin': datetime(2020, 1, 28, 15, 0, 0),
            'date_end': datetime(2020, 1, 30, 15, 0, 0),
        })
        self.assertFalse(practice.practice_confirmations_open)

        # no more seats available
        confirmation = self.env['practice.confirmation'].create({
            'name': 'Albert Test',
            'practice_id': practice.id,
        })
        confirmation.action_confirm()
        practice.write({
            'date_end': datetime(2020, 2, 1, 15, 0, 0),
            'seats_max': 1,
            'seats_limited': True,
        })
        self.assertEqual(practice.seats_available, 0)
        self.assertFalse(practice.practice_confirmations_open)

        # seats available are back
        confirmation.unlink()
        self.assertEqual(practice.seats_available, 1)
        self.assertTrue(practice.practice_confirmations_open)

        # but devices are expired
        device.write({'end_sale_datetime': datetime(2020, 1, 30, 15, 0, 0)})
        self.assertTrue(device.is_expired)
        self.assertFalse(practice.practice_confirmations_open)

    @users('user_practicemanager')
    def test_practice_ongoing(self):
        practice_1 = self.env['practice.practice'].create({
            'name': 'Test Practice 1',
            'date_begin': datetime(2020, 1, 25, 8, 0, 0),
            'date_end': datetime(2020, 2, 1, 18, 0, 0),
        })
        self.assertTrue(practice_1.is_ongoing)
        ongoing_practice_ids = self.env['practice.practice']._search([('is_ongoing', '=', True)])
        self.assertIn(practice_1.id, ongoing_practice_ids)

        practice_1.update({'date_begin': datetime(2020, 2, 1, 9, 0, 0)})
        self.assertFalse(practice_1.is_ongoing)
        ongoing_practice_ids = self.env['practice.practice']._search([('is_ongoing', '=', True)])
        self.assertNotIn(practice_1.id, ongoing_practice_ids)

        practice_2 = self.env['practice.practice'].create({
            'name': 'Test Practice 2',
            'date_begin': datetime(2020, 1, 25, 8, 0, 0),
            'date_end': datetime(2020, 1, 28, 8, 0, 0),
        })
        self.assertFalse(practice_2.is_ongoing)
        finished_or_upcoming_practice_ids = self.env['practice.practice']._search([('is_ongoing', '=', False)])
        self.assertIn(practice_2.id, finished_or_upcoming_practice_ids)

        practice_2.update({'date_end': datetime(2020, 2, 2, 8, 0, 1)})
        self.assertTrue(practice_2.is_ongoing)
        finished_or_upcoming_practice_ids = self.env['practice.practice']._search([('is_ongoing', '=', False)])
        self.assertNotIn(practice_2.id, finished_or_upcoming_practice_ids)

    @users('user_practicemanager')
    def test_practice_seats(self):
        practice_type = self.practice_type_complex.with_user(self.env.user)
        practice = self.env['practice.practice'].create({
            'name': 'Practice Update Type',
            'practice_type_id': practice_type.id,
            'date_begin': FieldsDatetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': FieldsDatetime.to_string(datetime.today() + timedelta(days=15)),
        })

        self.assertEqual(practice.address_id, self.env.user.company_id.partner_id)
        # seats: coming from practice type configuration
        self.assertTrue(practice.seats_limited)
        self.assertEqual(practice.seats_available, practice.practice_type_id.seats_max)
        self.assertEqual(practice.seats_unconfirmed, 0)
        self.assertEqual(practice.seats_reserved, 0)
        self.assertEqual(practice.seats_used, 0)
        self.assertEqual(practice.seats_expected, 0)

        # create confirmation in order to check the seats computation
        self.assertTrue(practice.auto_confirm)
        for x in range(5):
            reg = self.env['practice.confirmation'].create({
                'practice_id': practice.id,
                'name': 'reg_open',
            })
            self.assertEqual(reg.state, 'open')
        reg_draft = self.env['practice.confirmation'].create({
            'practice_id': practice.id,
            'name': 'reg_draft',
        })
        reg_draft.write({'state': 'draft'})
        reg_done = self.env['practice.confirmation'].create({
            'practice_id': practice.id,
            'name': 'reg_done',
        })
        reg_done.write({'state': 'done'})
        self.assertEqual(practice.seats_available, practice.practice_type_id.seats_max - 6)
        self.assertEqual(practice.seats_unconfirmed, 1)
        self.assertEqual(practice.seats_reserved, 5)
        self.assertEqual(practice.seats_used, 1)
        self.assertEqual(practice.seats_expected, 7)


class TestPracticeConfirmationData(TestPracticeCommon):

    @users('user_practicemanager')
    def test_confirmation_partner_sync(self):
        """ Test confirmation computed fields about partner """
        test_email = '"Nibbler In Space" <nibbler@futurama.example.com>'
        test_phone = '0456001122'

        practice = self.env['practice.practice'].browse(self.practice_0.ids)
        customer = self.env['res.partner'].browse(self.practice_customer.id)

        # take all from partner
        practice.write({
            'confirmation_ids': [(0, 0, {
                'partner_id': customer.id,
            })]
        })
        new_reg = practice.confirmation_ids[0]
        self.assertEqual(new_reg.partner_id, customer)
        self.assertEqual(new_reg.name, customer.name)
        self.assertEqual(new_reg.email, customer.email)
        self.assertEqual(new_reg.phone, customer.phone)

        # partial update
        practice.write({
            'confirmation_ids': [(0, 0, {
                'partner_id': customer.id,
                'name': 'Nibbler In Space',
                'email': test_email,
            })]
        })
        new_reg = practice.confirmation_ids.sorted()[0]
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
        practice.write({
            'confirmation_ids': [(0, 0, {
                'name': 'Nibbler In Space',
                'phone': test_phone,
            })]
        })
        new_reg = practice.confirmation_ids.sorted()[0]
        self.assertEqual(new_reg.name, 'Nibbler In Space')
        self.assertEqual(new_reg.email, False)
        self.assertEqual(new_reg.phone, test_phone)
        new_reg.write({'partner_id': customer.id})
        self.assertEqual(new_reg.partner_id, customer)
        self.assertEqual(new_reg.name, 'Nibbler In Space')
        self.assertEqual(new_reg.email, customer.email)
        self.assertEqual(new_reg.phone, test_phone)

    @users('user_practicemanager')
    def test_confirmation_partner_sync_company(self):
        """ Test synchronization involving companies """
        practice = self.env['practice.practice'].browse(self.practice_0.ids)
        customer = self.env['res.partner'].browse(self.practice_customer.id)

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
        practice.write({
            'confirmation_ids': [(0, 0, {
                'partner_id': customer.id,
            })]
        })
        new_reg = practice.confirmation_ids[0]
        self.assertEqual(new_reg.partner_id, customer)
        self.assertEqual(new_reg.name, contact.name)
        self.assertEqual(new_reg.email, contact.email)
        self.assertEqual(new_reg.phone, contact.phone)


class TestPracticeDeviceData(TestPracticeCommon):

    def setUp(self):
        super(TestPracticeDeviceData, self).setUp()
        self.device_date_patcher = patch('odoo.addons.practice.models.practice_device.fields.Date', wraps=FieldsDate)
        self.device_date_patcher_mock = self.device_date_patcher.start()
        self.device_date_patcher_mock.context_today.return_value = date(2020, 1, 31)
        self.device_datetime_patcher = patch('odoo.addons.practice.models.practice_device.fields.Datetime', wraps=FieldsDatetime)
        self.device_datetime_patcher_mock = self.device_datetime_patcher.start()
        self.device_datetime_patcher_mock.now.return_value = datetime(2020, 1, 31, 10, 0, 0)

    def tearDown(self):
        super(TestPracticeDeviceData, self).tearDown()
        self.device_date_patcher.stop()
        self.device_datetime_patcher.stop()

    @users('user_practicemanager')
    def test_practice_device_fields(self):
        """ Test practice device fields synchronization """
        practice = self.practice_0.with_user(self.env.user)
        practice.write({
            'practice_device_ids': [
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
        first_device = practice.practice_device_ids.filtered(lambda t: t.name == 'First Device')
        second_device = practice.practice_device_ids.filtered(lambda t: t.name == 'Second Device')

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

        #test if practice start/end dates are taking datetime fields (hours, minutes, seconds) into account
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


class TestPracticeTypeData(TestPracticeCommon):

    @users('user_practicemanager')
    def test_practice_type_fields(self):
        """ Test practice type fields synchronization """
        # create test type and ensure its initial values
        practice_type = self.env['practice.type'].create({
            'name': 'Testing fields computation',
            'has_seats_limitation': True,
            'seats_max': 30,
        })
        self.assertTrue(practice_type.has_seats_limitation)
        self.assertEqual(practice_type.seats_max, 30)

        # reset seats limitation
        practice_type.write({'has_seats_limitation': False})
        self.assertFalse(practice_type.has_seats_limitation)
        self.assertEqual(practice_type.seats_max, 0)
