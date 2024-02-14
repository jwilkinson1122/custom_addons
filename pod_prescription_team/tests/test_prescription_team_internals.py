# -*- coding: utf-8 -*-


from odoo import exceptions
from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.pod_prescription_team.tests.common import TestPrescriptionMC
from odoo.tests.common import users, TransactionCase
from odoo.tools import mute_logger


class TestCornerCases(TransactionCase):

    def setUp(self):
        super(TestCornerCases, self).setUp()
        self.user_prescription_leads = mail_new_test_user(
            self.env, login='user_prescription_leads',
            name='Laetitia Prescription Leads', email='crm_leads@test.example.com',
            company_id=self.env.user.company_id.id,
            notification_type='inbox',
            groups='pod_prescription_team.group_prescription_personnel_all_leads,base.group_partner_manager',
        )
        self.prescription_team_1 = self.env['crm.team'].create({
            'name': 'Test Prescription Team',
            'sequence': 5,
            'company_id': False,
            'user_id': self.env.user.id,
        })

    def test_unicity(self):
        """ Archived memberships should be removed when detecting duplicates.
        Creating duplicates should raise unicity constraint.

        Note: redoing the data set to avoid clashing with SavepointCase as
        we expect a db-level assert """
        prescription_team_1_m1 = self.env['crm.team.member'].create({
            'user_id': self.user_prescription_leads.id,
            'crm_team_id': self.prescription_team_1.id,
        })

        prescription_team_1_m1.write({'active': False})
        prescription_team_1_m1.flush_recordset()

        prescription_team_1_m2 = self.env['crm.team.member'].create({
            'user_id': self.user_prescription_leads.id,
            'crm_team_id': self.prescription_team_1.id,
        })

        found = self.env['crm.team.member'].search([
            ('user_id', '=', self.user_prescription_leads.id),
            ('crm_team_id', '=', self.prescription_team_1.id),
        ])
        self.assertEqual(found, prescription_team_1_m2)

        with self.assertRaises(exceptions.UserError), mute_logger('odoo.sql_db'):
            self.env['crm.team.member'].create({
                'user_id': self.user_prescription_leads.id,
                'crm_team_id': self.prescription_team_1.id,
            })

    def test_unicity_multicreate(self):
        """ Test constraint works with creating duplicates in the same create
        method. """
        with self.assertRaises(exceptions.UserError), mute_logger('odoo.sql_db'):
            self.env['crm.team.member'].create([
                {'user_id': self.user_prescription_leads.id, 'crm_team_id': self.prescription_team_1.id},
                {'user_id': self.user_prescription_leads.id, 'crm_team_id': self.prescription_team_1.id}
            ])


class TestSecurity(TestPrescriptionMC):

    @users('user_prescription_leads')
    def test_team_access(self):
        prescription_team = self.prescription_team_1.with_user(self.env.user)

        prescription_team.read(['name'])
        for member in prescription_team.member_ids:
            member.read(['name'])

        with self.assertRaises(exceptions.AccessError):
            prescription_team.write({'name': 'Trolling'})

        for membership in prescription_team.crm_team_member_ids:
            membership.read(['name'])
            with self.assertRaises(exceptions.AccessError):
                membership.write({'active': False})

        with self.assertRaises(exceptions.AccessError):
            prescription_team.write({'member_ids': [(5, 0)]})

    @users('user_prescription_leads')
    def test_team_multi_company(self):
        self.prescription_team_1.with_user(self.env.user).read(['name'])
        with self.assertRaises(exceptions.AccessError):
            self.team_c2.with_user(self.env.user).read(['name'])
