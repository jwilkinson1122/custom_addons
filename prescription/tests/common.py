# -*- coding: utf-8 -*-


from datetime import datetime, timedelta

from odoo import fields
from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.tests import common


class TestPrescriptionCommon(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestPrescriptionCommon, cls).setUpClass()

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
        cls.user_prescriptionconfirmationdesk = mail_new_test_user(
            cls.env, login='user_prescriptionconfirmationdesk',
            name='Ursule PrescriptionConfirmation', email='ursule.prescriptionconfirmation@test.example.com',
            tz='Europe/Brussels', notification_type='inbox',
            company_id=cls.env.ref("base.main_company").id,
            groups='base.group_user,prescription.group_prescription_confirmation_desk',
        )
        cls.user_prescriptionuser = mail_new_test_user(
            cls.env, login='user_prescriptionuser',
            name='Ursule PrescriptionUser', email='ursule.prescriptionuser@test.example.com',
            tz='Europe/Brussels', notification_type='inbox',
            company_id=cls.env.ref("base.main_company").id,
            groups='base.group_user,prescription.group_prescription_user',
        )
        cls.user_prescriptionmanager = mail_new_test_user(
            cls.env, login='user_prescriptionmanager',
            name='Martine PrescriptionManager', email='martine.prescriptionmanager@test.example.com',
            tz='Europe/Brussels', notification_type='inbox',
            company_id=cls.env.ref("base.main_company").id,
            groups='base.group_user,prescription.group_prescription_manager',
        )

        cls.prescription_customer = cls.env['res.partner'].create({
            'name': 'Constantin Customer',
            'email': 'constantin@test.example.com',
            'country_id': cls.env.ref('base.be').id,
            'phone': '0485112233',
            'mobile': False,
        })
        cls.prescription_customer2 = cls.env['res.partner'].create({
            'name': 'Constantin Customer 2',
            'email': 'constantin2@test.example.com',
            'country_id': cls.env.ref('base.be').id,
            'phone': '0456987654',
            'mobile': '0456654321',
        })

        cls.prescription_type_complex = cls.env['prescription.type'].create({
            'name': 'Update Type',
            'auto_confirm': True,
            'has_seats_limitation': True,
            'seats_max': 30,
            'default_timezone': 'Europe/Paris',
            'prescription_type_device_ids': [(0, 0, {
                    'name': 'First Device',
                }), (0, 0, {
                    'name': 'Second Device',
                })
            ],
            'prescription_type_mail_ids': [
                (0, 0, {  # right at subscription
                    'interval_unit': 'now',
                    'interval_type': 'after_sub',
                    'template_ref': 'mail.template,%i' % cls.env['ir.model.data']._xmlid_to_res_id('prescription.prescription_subscription')}),
                (0, 0, {  # 1 days before prescription
                    'interval_nbr': 1,
                    'interval_unit': 'days',
                    'interval_type': 'before_prescription',
                    'template_ref': 'mail.template,%i' % cls.env['ir.model.data']._xmlid_to_res_id('prescription.prescription_reminder')}),
            ],
        })
        cls.prescription_0 = cls.env['prescription.prescription'].create({
            'name': 'TestPrescription',
            'auto_confirm': True,
            'date_begin': fields.Datetime.to_string(datetime.today() + timedelta(days=1)),
            'date_end': fields.Datetime.to_string(datetime.today() + timedelta(days=15)),
            'date_tz': 'Europe/Brussels',
        })

        # set country in order to format Belgian numbers
        cls.prescription_0.company_id.write({'country_id': cls.env.ref('base.be').id})

    @classmethod
    def _create_confirmations(cls, prescription, reg_count):
        # create some confirmations
        confirmations = cls.env['prescription.confirmation'].create([{
            'prescription_id': prescription.id,
            'name': 'Test Confirmation %s' % x,
            'email': '_test_reg_%s@example.com' % x,
            'phone': '04560000%s%s' % (x, x),
        } for x in range(0, reg_count)])
        return confirmations
