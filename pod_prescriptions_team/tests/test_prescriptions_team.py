# -*- coding: utf-8 -*-


from odoo import exceptions
from odoo.tests import tagged, users

from odoo.addons.pod_prescriptions_team.tests.common import PrescriptionsTeamCommon, TestPrescriptionsCommon, TestPrescriptionsMC


class TestDefaultTeam(TestPrescriptionsCommon):
    """Tests to check if correct default team is found."""

    @classmethod
    def setUpClass(cls):
        """Set up data for default team tests."""
        super(TestDefaultTeam, cls).setUpClass()
        cls.env['ir.config_parameter'].set_param('pod_prescriptions_team.membership_multi', True)

        # Prescriptionsmen organization
        # ------------------------------------------------------------
        # Role: M (team member) R (team manager)
        # SALESMAN---------------prescriptions_team_1---C2Team1---LowSequ---Team3
        # admin------------------M-------------- --------- ---------
        # user_prescriptions_manager-----R-------------- --------- ---------R
        # user_prescriptions_leads-------M-------------- ---------M---------
        # user_prescriptions_personnel----/-------------- --------- ---------

        # Prescriptions teams organization
        # ------------------------------------------------------------
        # SALESTEAM-----------SEQU-----COMPANY
        # LowSequence---------0--------False
        # C2Team1-------------1--------C2
        # Team3---------------3--------Main
        # prescriptions_team_1--------5--------False
        # data----------------9999-----??

        cls.company_2 = cls.env['res.company'].create({
            'name': 'New Test Company',
            'email': 'company.2@test.example.com',
            'country_id': cls.env.ref('base.fr').id,
        })
        cls.team_c2 = cls.env['crm.team'].create({
            'name': 'C2 Team1',
            'sequence': 1,
            'company_id': cls.company_2.id,
            'user_id': False,
        })
        cls.team_sequence = cls.env['crm.team'].create({
            'company_id': False,
            'name': 'Team LowSequence',
            'member_ids': [(4, cls.user_prescriptions_leads.id)],
            'sequence': 0,
            'user_id': False,
        })
        cls.team_responsible = cls.env['crm.team'].create({
            'company_id': cls.company_main.id,
            'name': 'Team 3',
            'user_id': cls.user_prescriptions_manager.id,
            'sequence': 3,
        })

    def test_default_team_fallback(self):
        """ Test fallbacks when computing default team without any memberships:
        domain, order """
        self.prescriptions_team_1.member_ids = [(5,)]
        self.team_sequence.member_ids = [(5,)]
        (self.prescriptions_team_1 + self.team_sequence).flush_model()
        self.assertFalse(self.env['crm.team.member'].search([('user_id', '=', self.user_prescriptions_leads.id)]))

        # default is better sequence matching company criterion
        with self.with_user('user_prescriptions_leads'):
            team = self.env['crm.team']._get_default_team_id()
            self.assertEqual(team, self.team_sequence)

        # next one is team_responsible with sequence = 3 (team_c2 is in another company)
        self.team_sequence.active = False
        with self.with_user('user_prescriptions_leads'):
            team = self.env['crm.team']._get_default_team_id()
            self.assertEqual(team, self.team_responsible)

        self.user_prescriptions_leads.write({
            'company_ids': [(4, self.company_2.id)],
            'company_id': self.company_2.id,
        })
        # multi company: switch company
        self.user_prescriptions_leads.write({
            'company_id': self.company_2.id,
            'company_ids': [(4, self.company_2.id)],
        })
        with self.with_user('user_prescriptions_leads'):
            team = self.env['crm.team']._get_default_team_id()
            self.assertEqual(team, self.team_c2)

    def test_default_team_member(self):
        """ Test default team choice based on sequence, when having several
        possible choices due to membership """
        with self.with_user('user_prescriptions_leads'):
            team = self.env['crm.team']._get_default_team_id()
            self.assertEqual(team, self.team_sequence)

        self.team_sequence.member_ids = [(5,)]
        self.team_sequence.flush_model()
        with self.with_user('user_prescriptions_leads'):
            team = self.env['crm.team']._get_default_team_id()
            self.assertEqual(team, self.prescriptions_team_1)

        # responsible with lower sequence better than member with higher sequence
        self.team_responsible.user_id = self.user_prescriptions_leads.id
        with self.with_user('user_prescriptions_leads'):
            team = self.env['crm.team']._get_default_team_id()
            self.assertEqual(team, self.team_responsible)

        # in case of same sequence: take latest team
        self.team_responsible.sequence = self.prescriptions_team_1.sequence
        with self.with_user('user_prescriptions_leads'):
            team = self.env['crm.team']._get_default_team_id()
            self.assertEqual(team, self.team_responsible)

    def test_default_team_wcontext(self):
        """ Test default team choice when having a value in context """
        with self.with_user('user_prescriptions_leads'):
            team = self.env['crm.team']._get_default_team_id()
            self.assertEqual(team, self.team_sequence)

            team = self.env['crm.team'].with_context(
                default_team_id=self.prescriptions_team_1.id
            )._get_default_team_id()
            self.assertEqual(
                team, self.prescriptions_team_1,
                'PrescriptionsTeam: default takes over ordering when member / responsible'
            )

        # remove all memberships
        self.prescriptions_team_1.member_ids = [(5,)]
        self.team_sequence.member_ids = [(5,)]
        (self.prescriptions_team_1 + self.team_sequence).flush_model()
        self.assertFalse(self.env['crm.team.member'].search([('user_id', '=', self.user_prescriptions_leads.id)]))

        with self.with_user('user_prescriptions_leads'):
            team = self.env['crm.team']._get_default_team_id()
            self.assertEqual(team, self.team_sequence)

            team = self.env['crm.team'].with_context(
                default_team_id=self.prescriptions_team_1.id
            )._get_default_team_id()
            self.assertEqual(
                team, self.prescriptions_team_1,
                'PrescriptionsTeam: default taken into account when no member / responsible'
            )

class TestMultiCompany(TestPrescriptionsMC):
    """Tests to check multi company management with prescriptions team and their
    members. """

    @users('user_prescriptions_manager')
    def test_team_members(self):
        """ Test update of team users involving company check """
        team_c2 = self.env['crm.team'].browse(self.team_c2.id)
        team_c2.write({'name': 'Manager Update'})
        self.assertEqual(team_c2.member_ids, self.env['res.users'])

        # can add someone from same company
        self.env.user.write({'company_id': self.company_2.id})
        team_c2.write({'member_ids': [(4, self.env.user.id)]})
        self.assertEqual(team_c2.member_ids, self.env.user)

        # cannot add someone from another company
        with self.assertRaises(exceptions.UserError):
            team_c2.write({'member_ids': [(4, self.user_prescriptions_personnel.id)]})

        # reset members, change company
        team_c2.write({'member_ids': [(5, 0)], 'company_id': self.company_main.id})
        self.assertEqual(team_c2.member_ids, self.env['res.users'])
        team_c2.write({'member_ids': [(4, self.user_prescriptions_personnel.id)]})
        self.assertEqual(team_c2.member_ids, self.user_prescriptions_personnel)

        # cannot change company as it breaks memberships mc check
        with self.assertRaises(exceptions.UserError):
            team_c2.write({'company_id': self.company_2.id})

    @users('user_prescriptions_manager')
    def test_team_memberships(self):
        """ Test update of team member involving company check """
        team_c2 = self.env['crm.team'].browse(self.team_c2.id)
        team_c2.write({'name': 'Manager Update'})
        self.assertEqual(team_c2.member_ids, self.env['res.users'])

        # can add someone from same company
        self.env.user.write({'company_id': self.company_2.id})
        team_c2.write({'crm_team_member_ids': [(0, 0, {'user_id': self.env.user.id})]})
        self.assertEqual(team_c2.member_ids, self.env.user)

        # cannot add someone from another company
        with self.assertRaises(exceptions.UserError):
            team_c2.write({'crm_team_member_ids': [(0, 0, {'user_id': self.user_prescriptions_personnel.id})]})

        # reset members, change company
        team_c2.write({'member_ids': [(5, 0)], 'company_id': self.company_main.id})
        self.assertEqual(team_c2.member_ids, self.env['res.users'])
        team_c2.write({'crm_team_member_ids': [(0, 0, {'user_id': self.user_prescriptions_personnel.id})]})
        self.assertEqual(team_c2.member_ids, self.user_prescriptions_personnel)

        # cannot change company as it breaks memberships mc check
        with self.assertRaises(exceptions.UserError):
            team_c2.write({'company_id': self.company_2.id})


@tagged('post_install', '-at_install')
class TestAccessRights(PrescriptionsTeamCommon):

    @users('personnelager')
    def test_access_prescriptions_manager(self):
        """ Test prescriptions manager's access rights """
        # Manager can create a Prescriptions Team
        india_channel = self.env['crm.team'].with_context(tracking_disable=True).create({
            'name': 'India',
        })
        self.assertIn(
            india_channel.id, self.env['crm.team'].search([]).ids,
            'Prescriptions manager should be able to create a Prescriptions Team')

        # Manager can edit a Prescriptions Team
        india_channel.write({'name': 'new_india'})
        self.assertEqual(
            india_channel.name, 'new_india',
            'Prescriptions manager should be able to edit a Prescriptions Team')

        # Manager can delete a Prescriptions Team
        india_channel.unlink()
        self.assertNotIn(
            india_channel.id, self.env['crm.team'].search([]).ids,
            'Prescriptions manager should be able to delete a Prescriptions Team')
