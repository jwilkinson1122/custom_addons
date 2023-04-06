# -*- coding: utf-8 -*-


from datetime import datetime, timedelta

from odoo import fields
from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.tests import common


class TestPracticeCommon(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestPracticeCommon, cls).setUpClass()

        # Test users to use through the various tests
        cls.user_portal = mail_new_test_user(
            cls.env, login='portal_test',
            name='Patrick Portal', email='patrick.portal@test.example.com',
            notification_type='email', company_id=cls.env.ref("base.main_company").id,
            groups='base.group_portal')
        cls.user_employee = mail_new_test_user(
            cls.env, login='user_employee',
            name='Eglantine Employee', email='eglantine.employee@test.example.com',
            tz='Europe/Brussels', notification_type='inbox',
            company_id=cls.env.ref("base.main_company").id,
            groups='base.group_user',
        )
        cls.user_practiceconfirmationdesk = mail_new_test_user(
            cls.env, login='user_practiceconfirmationdesk',
            name='Ursule PracticeConfirmation', email='ursule.practiceconfirmation@test.example.com',
            tz='Europe/Brussels', notification_type='inbox',
            company_id=cls.env.ref("base.main_company").id,
            groups='base.group_user,practice.group_practice_confirmation_desk',
        )
        cls.user_practiceuser = mail_new_test_user(
            cls.env, login='user_practiceuser',
            name='Ursule PracticeUser', email='ursule.practiceuser@test.example.com',
            tz='Europe/Brussels', notification_type='inbox',
            company_id=cls.env.ref("base.main_company").id,
            groups='base.group_user,practice.group_practice_user',
        )
        cls.user_practicemanager = mail_new_test_user(
            cls.env, login='user_practicemanager',
            name='Martine PracticeManager', email='martine.practicemanager@test.example.com',
            tz='Europe/Brussels', notification_type='inbox',
            company_id=cls.env.ref("base.main_company").id,
            groups='base.group_user,practice.group_practice_manager',
        )

        cls.practice_customer = cls.env['res.partner'].create({
            'name': 'Constantin Customer',
            'email': 'constantin@test.example.com',
            'country_id': cls.env.ref('base.be').id,
            'phone': '0485112233',
            'mobile': False,
        })
        cls.practice_customer2 = cls.env['res.partner'].create({
            'name': 'Constantin Customer 2',
            'email': 'constantin2@test.example.com',
            'country_id': cls.env.ref('base.be').id,
            'phone': '0456987654',
            'mobile': '0456654321',
        })

        cls.practice_type_complex = cls.env['practice.type'].create({
            'name': 'Update Type',
            'auto_confirm': True,
            'has_seats_limitation': True,
            'seats_max': 30,
            'default_timezone': 'Europe/Paris',
            'practice_type_device_ids': [(0, 0, {
                    'name': 'First Device',
                }), (0, 0, {
                    'name': 'Second Device',
                })
            ],
            'practice_type_mail_ids': [
                (0, 0, {  # right at subscription
                    'interval_unit': 'now',
                    'interval_type': 'after_sub',
                    'template_ref': 'mail.template,%i' % cls.env['ir.model.data']._xmlid_to_res_id('practice.practice_subscription')}),
                (0, 0, {  # 1 days before practice
                    'interval_nbr': 1,
                    'interval_unit': 'days',
                    'interval_type': 'before_practice',
                    'template_ref': 'mail.template,%i' % cls.env['ir.model.data']._xmlid_to_res_id('practice.practice_reminder')}),
            ],
        })
        cls.practice_0 = cls.env['practice.practice'].create({
            'name': 'TestPractice',
            'auto_confirm': True,
            'date_begin': fields.Datetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': fields.Datetime.to_string(datetime.today() + timedelta(days=15)),
            'date_tz': 'Europe/Brussels',
        })

        # set country in order to format Belgian numbers
        cls.practice_0.company_id.write({'country_id': cls.env.ref('base.be').id})

    @classmethod
    def _create_confirmations(cls, practice, reg_count):
        # create some confirmations
        confirmations = cls.env['practice.confirmation'].create([{
            'practice_id': practice.id,
            'name': 'Test Confirmation %s' % x,
            'email': '_test_reg_%s@example.com' % x,
            'phone': '04560000%s%s' % (x, x),
        } for x in range(0, reg_count)])
        return confirmations
