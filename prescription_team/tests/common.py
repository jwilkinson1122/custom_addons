# -*- coding: utf-8 -*-


from odoo.tests import TransactionCase

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT

class PrescriptionTeamCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env['base'].with_context(**DISABLED_MAIL_CONTEXT).env

        cls.group_prescription_prescriptionman = cls.env.ref('prescription_team.group_prescription_prescriptionman')
        cls.group_prescription_manager = cls.env.ref('prescription_team.group_prescription_manager')

        cls.prescription_user = cls.env['res.users'].create({
            'name': 'Test Prescriptionman',
            'login': 'prescriptionman',
            'password': 'prescriptionman',
            'email': 'default_user_prescriptionman@example.com',
            'signature': '--\nMark',
            'notification_type': 'email',
            'groups_id': [(6, 0, cls.group_prescription_prescriptionman.ids)],
        })
        cls.prescription_manager = cls.env['res.users'].create({
            'name': 'Test Prescription Manager',
            'login': 'prescriptionmanager',
            'password': 'prescriptionmanager',
            'email': 'default_user_prescriptionmanager@example.com',
            'signature': '--\nDamien',
            'notification_type': 'email',
            'groups_id': [(6, 0, cls.group_prescription_manager.ids)],
        })
        cls.prescription_team = cls.env['crm.team'].create({
            'name': 'Test Prescription Team',
        })
        # Disable other teams (demo data/existing data)
        cls.env['crm.team'].search([
            ('id', '!=', cls.prescription_team.id),
        ]).action_archive()


class TestPrescriptionCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestPrescriptionCommon, cls).setUpClass()
        cls.env['ir.config_parameter'].set_param('prescription_team.membership_multi', False)

        # Prescriptionmen organization
        # ------------------------------------------------------------
        # Role: M (team member) R (team manager)
        # SALESMAN---------------prescription_team_1
        # admin------------------M-----------
        # user_prescription_manager-----R-----------
        # user_prescription_leads-------M-----------
        # user_prescription_prescriptionman----/-----------

        # Prescription teams organization
        # ------------------------------------------------------------
        # SALESTEAM-----------SEQU-----COMPANY
        # prescription_team_1--------5--------False
        # data----------------9999-----??

        cls.company_main = cls.env.user.company_id
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.user_prescription_manager = mail_new_test_user(
            cls.env, login='user_prescription_manager',
            name='Martin Prescription Manager', email='crm_manager@test.example.com',
            company_id=cls.company_main.id,
            notification_type='inbox',
            groups='prescription_team.group_prescription_manager,base.group_partner_manager',
        )
        cls.user_prescription_leads = mail_new_test_user(
            cls.env, login='user_prescription_leads',
            name='Laetitia Prescription Leads', email='crm_leads@test.example.com',
            company_id=cls.company_main.id,
            notification_type='inbox',
            groups='prescription_team.group_prescription_prescriptionman_all_leads,base.group_partner_manager',
        )
        cls.user_prescription_prescriptionman = mail_new_test_user(
            cls.env, login='user_prescription_prescriptionman',
            name='Orteil Prescription Own', email='crm_prescriptionman@test.example.com',
            company_id=cls.company_main.id,
            notification_type='inbox',
            groups='prescription_team.group_prescription_prescriptionman',
        )

        cls.env['crm.team'].search([]).write({'sequence': 9999})
        cls.prescription_team_1 = cls.env['crm.team'].create({
            'name': 'Test Prescription Team',
            'sequence': 5,
            'company_id': False,
            'user_id': cls.user_prescription_manager.id,
        })
        cls.prescription_team_1_m1 = cls.env['crm.team.member'].create({
            'user_id': cls.user_prescription_leads.id,
            'crm_team_id': cls.prescription_team_1.id,
        })
        cls.prescription_team_1_m2 = cls.env['crm.team.member'].create({
            'user_id': cls.user_admin.id,
            'crm_team_id': cls.prescription_team_1.id,
        })


class TestPrescriptionMC(TestPrescriptionCommon):
    """ Multi Company / Multi Prescription Team environment """

    @classmethod
    def setUpClass(cls):
        """ Teams / Company

          * prescription_team_1: False
          * team_c2: company_2
          * team_mc: company_main
        """
        super(TestPrescriptionMC, cls).setUpClass()
        cls.company_2 = cls.env['res.company'].create({
            'name': 'New Test Company',
            'email': 'company.2@test.example.com',
            'country_id': cls.env.ref('base.fr').id,
        })
        cls.team_c2 = cls.env['crm.team'].create({
            'name': 'C2 Team1',
            'sequence': 1,
            'user_id': False,
            'company_id': cls.company_2.id,
        })
        cls.team_mc = cls.env['crm.team'].create({
            'name': 'MainCompany Team',
            'user_id': cls.user_admin.id,
            'sequence': 3,
            'company_id': cls.company_main.id
        })

        # admin and prescription manager belong to new company also
        (cls.user_admin | cls.user_prescription_manager).write({
            'company_ids': [(4, cls.company_2.id)]
        })
