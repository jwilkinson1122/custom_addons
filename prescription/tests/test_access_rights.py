# -*- coding: utf-8 -*-


from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseUsersCommon
from odoo.addons.prescription.tests.common import PrescriptionCommon


@tagged('post_install', '-at_install')
class TestAccessRights(BaseUsersCommon, PrescriptionCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.prescription_user2 = cls.env['res.users'].create({
            'name': 'personnel_2',
            'login': 'personnel_2',
            'email': 'default_user_personnel_2@example.com',
            'signature': '--\nMark',
            'notification_type': 'email',
            'groups_id': [(6, 0, cls.group_prescription_personnel.ids)],
        })

        # Create the SO with a specific prescriptionperson
        cls.prescription.user_id = cls.prescription_user

    def test_access_prescription_manager(self):
        """ Test prescription manager's access rights """
        Prescription = self.env['prescription'].with_user(self.prescription_manager)
        so_as_prescription_manager = Prescription.browse(self.prescription.id)

        # Manager can see the SO which is assigned to another prescriptionperson
        so_as_prescription_manager.read()
        # Manager can change a prescriptionperson of the SO
        so_as_prescription_manager.write({'user_id': self.prescription_user2.id})

        # Manager can create the SO for other prescriptionperson
        prescription = Prescription.create({
            'partner_id': self.partner.id,
            'user_id': self.prescription_user.id
        })
        self.assertIn(
            prescription.id, Prescription.search([]).ids,
            'Prescription manager should be able to create the SO of other prescriptionperson')
        # Manager can confirm the SO
        prescription.action_confirm()
        # Manager can not delete confirmed SO
        with self.assertRaises(UserError), mute_logger('odoo.models.unlink'):
            prescription.unlink()

        # Manager can delete the SO of other prescriptionperson if SO is in 'draft' or 'cancel' state
        so_as_prescription_manager.unlink()
        self.assertNotIn(
            so_as_prescription_manager.id, Prescription.search([]).ids,
            'Prescription manager should be able to delete the SO')

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_access_prescription_person(self):
        """ Test Prescriptionperson's access rights """
        Prescription = self.env['prescription'].with_user(self.prescription_user2)
        so_as_prescriptionperson = Prescription.browse(self.prescription.id)

        # Prescriptionperson can see only their own prescription order
        with self.assertRaises(AccessError):
            so_as_prescriptionperson.read()

        # Now assign the SO to themselves
        # (using self.prescription to do the change as superuser)
        self.prescription.write({'user_id': self.prescription_user2.id})

        # The prescriptionperson is now able to read it
        so_as_prescriptionperson.read()
        # Prescriptionperson can change a Prescription Team of SO
        so_as_prescriptionperson.write({'team_id': self.prescription_team.id})

        # Prescriptionperson can't create a SO for other prescriptionperson
        with self.assertRaises(AccessError):
            self.env['prescription'].with_user(self.prescription_user2).create({
                'partner_id': self.partner.id,
                'user_id': self.prescription_user.id
            })

        # Prescriptionperson can't delete Prescription Orders
        with self.assertRaises(AccessError):
            so_as_prescriptionperson.unlink()

        # Prescriptionperson can confirm the SO
        so_as_prescriptionperson.action_confirm()

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_access_portal_user(self):
        """ Test portal user's access rights """
        Prescription = self.env['prescription'].with_user(self.user_portal)
        so_as_portal_user = Prescription.browse(self.prescription.id)

        # Portal user can see the confirmed SO for which they are assigned as a customer
        with self.assertRaises(AccessError):
            so_as_portal_user.read()

        self.prescription.partner_id = self.user_portal.partner_id
        self.prescription.action_confirm()
        # Portal user can't edit the SO
        with self.assertRaises(AccessError):
            so_as_portal_user.write({'team_id': self.prescription_team.id})
        # Portal user can't create the SO
        with self.assertRaises(AccessError):
            Prescription.create({
                'partner_id': self.partner.id,
            })
        # Portal user can't delete the SO which is in 'draft' or 'cancel' state
        self.prescription.action_cancel()
        with self.assertRaises(AccessError):
            so_as_portal_user.unlink()

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_access_employee(self):
        """ Test classic employee's access rights """
        Prescription = self.env['prescription'].with_user(self.user_internal)
        so_as_internal_user = Prescription.browse(self.prescription.id)

        # Employee can't see any SO
        with self.assertRaises(AccessError):
            so_as_internal_user.read()
        # Employee can't edit the SO
        with self.assertRaises(AccessError):
            so_as_internal_user.write({'team_id': self.prescription_team.id})
        # Employee can't create the SO
        with self.assertRaises(AccessError):
            Prescription.create({
                'partner_id': self.partner.id,
            })
        # Employee can't delete the SO
        with self.assertRaises(AccessError):
            so_as_internal_user.unlink()
