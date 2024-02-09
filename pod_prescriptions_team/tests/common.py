# -*- coding: utf-8 -*-


from odoo.tests import TransactionCase

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT

class PrescriptionsTeamCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env['base'].with_context(**DISABLED_MAIL_CONTEXT).env

        cls.group_prescriptions_personnel = cls.env.ref('pod_prescriptions_team.group_prescriptions_personnel')
        cls.group_prescriptions_manager = cls.env.ref('pod_prescriptions_team.group_prescriptions_manager')

        cls.prescriptions_user = cls.env['res.users'].create({
            'name': 'Test Prescriptionsman',
            'login': 'personnel',
            'password': 'personnel',
            'email': 'default_user_personnel@example.com',
            'signature': '--\nMark',
            'notification_type': 'email',
            'groups_id': [(6, 0, cls.group_prescriptions_personnel.ids)],
        })
        cls.prescriptions_manager = cls.env['res.users'].create({
            'name': 'Test Prescriptions Manager',
            'login': 'personnelager',
            'password': 'personnelager',
            'email': 'default_user_personnelager@example.com',
            'signature': '--\nDamien',
            'notification_type': 'email',
            'groups_id': [(6, 0, cls.group_prescriptions_manager.ids)],
        })
        cls.prescriptions_team = cls.env['crm.team'].create({
            'name': 'Test Prescriptions Team',
        })
        # Disable other teams (demo data/existing data)
        cls.env['crm.team'].search([
            ('id', '!=', cls.prescriptions_team.id),
        ]).action_archive()


class TestPrescriptionsCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestPrescriptionsCommon, cls).setUpClass()
        cls.env['ir.config_parameter'].set_param('pod_prescriptions_team.membership_multi', False)

        # Prescriptionsmen organization
        # ------------------------------------------------------------
        # Role: M (team member) R (team manager)
        # SALESMAN---------------prescriptions_team_1
        # admin------------------M-----------
        # user_prescriptions_manager-----R-----------
        # user_prescriptions_leads-------M-----------
        # user_prescriptions_personnel----/-----------

        # Prescriptions teams organization
        # ------------------------------------------------------------
        # SALESTEAM-----------SEQU-----COMPANY
        # prescriptions_team_1--------5--------False
        # data----------------9999-----??

        cls.company_main = cls.env.user.company_id
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.user_prescriptions_manager = mail_new_test_user(
            cls.env, login='user_prescriptions_manager',
            name='Martin Prescriptions Manager', email='crm_manager@test.example.com',
            company_id=cls.company_main.id,
            notification_type='inbox',
            groups='pod_prescriptions_team.group_prescriptions_manager,base.group_partner_manager',
        )
        cls.user_prescriptions_leads = mail_new_test_user(
            cls.env, login='user_prescriptions_leads',
            name='Laetitia Prescriptions Leads', email='crm_leads@test.example.com',
            company_id=cls.company_main.id,
            notification_type='inbox',
            groups='pod_prescriptions_team.group_prescriptions_personnel_all_leads,base.group_partner_manager',
        )
        cls.user_prescriptions_personnel = mail_new_test_user(
            cls.env, login='user_prescriptions_personnel',
            name='Orteil Prescriptions Own', email='crm_personnel@test.example.com',
            company_id=cls.company_main.id,
            notification_type='inbox',
            groups='pod_prescriptions_team.group_prescriptions_personnel',
        )

        cls.env['crm.team'].search([]).write({'sequence': 9999})
        cls.prescriptions_team_1 = cls.env['crm.team'].create({
            'name': 'Test Prescriptions Team',
            'sequence': 5,
            'company_id': False,
            'user_id': cls.user_prescriptions_manager.id,
        })
        cls.prescriptions_team_1_m1 = cls.env['crm.team.member'].create({
            'user_id': cls.user_prescriptions_leads.id,
            'crm_team_id': cls.prescriptions_team_1.id,
        })
        cls.prescriptions_team_1_m2 = cls.env['crm.team.member'].create({
            'user_id': cls.user_admin.id,
            'crm_team_id': cls.prescriptions_team_1.id,
        })


class TestPrescriptionsMC(TestPrescriptionsCommon):
    """ Multi Company / Multi Prescriptions Team environment """

    @classmethod
    def setUpClass(cls):
        """ Teams / Company

          * prescriptions_team_1: False
          * team_c2: company_2
          * team_mc: company_main
        """
        super(TestPrescriptionsMC, cls).setUpClass()
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

        # admin and prescriptions manager belong to new company also
        (cls.user_admin | cls.user_prescriptions_manager).write({
            'company_ids': [(4, cls.company_2.id)]
        })
