# -*- coding: utf-8 -*-


from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseUsersCommon
from odoo.addons.pod_prescriptions.tests.common import PrescriptionCommon


@tagged('post_install', '-at_install')
class TestAccessRights(BaseUsersCommon, PrescriptionCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.prescriptions_user2 = cls.env['res.users'].create({
            'name': 'prescriptionsman_2',
            'login': 'prescriptionsman_2',
            'email': 'default_user_prescriptionsman_2@example.com',
            'signature': '--\nMark',
            'notification_type': 'email',
            'groups_id': [(6, 0, cls.group_prescriptions_prescriptionsman.ids)],
        })

        # Create the RX with a specific prescriptionsperson
        cls.prescriptions_order.user_id = cls.prescriptions_user

    def test_access_prescriptions_manager(self):
        """ Test prescriptions manager's access rights """
        PrescriptionOrder = self.env['prescriptions.order'].with_user(self.prescriptions_manager)
        rx_as_prescriptions_manager = PrescriptionOrder.browse(self.prescriptions_order.id)

        # Manager can see the RX which is assigned to another prescriptionsperson
        rx_as_prescriptions_manager.read()
        # Manager can change a prescriptionsperson of the RX
        rx_as_prescriptions_manager.write({'user_id': self.prescriptions_user2.id})

        # Manager can create the RX for other prescriptionsperson
        prescriptions_order = PrescriptionOrder.create({
            'partner_id': self.partner.id,
            'user_id': self.prescriptions_user.id
        })
        self.assertIn(
            prescriptions_order.id, PrescriptionOrder.search([]).ids,
            'Prescriptions manager should be able to create the RX of other prescriptionsperson')
        # Manager can confirm the RX
        prescriptions_order.action_confirm()
        # Manager can not delete confirmed RX
        with self.assertRaises(UserError), mute_logger('odoo.models.unlink'):
            prescriptions_order.unlink()

        # Manager can delete the RX of other prescriptionsperson if RX is in 'draft' or 'cancel' state
        rx_as_prescriptions_manager.unlink()
        self.assertNotIn(
            rx_as_prescriptions_manager.id, PrescriptionOrder.search([]).ids,
            'Prescriptions manager should be able to delete the RX')

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_access_prescriptions_person(self):
        """ Test Prescriptionsperson's access rights """
        PrescriptionOrder = self.env['prescriptions.order'].with_user(self.prescriptions_user2)
        rx_as_prescriptionsperson = PrescriptionOrder.browse(self.prescriptions_order.id)

        # Prescriptionsperson can see only their own prescriptions order
        with self.assertRaises(AccessError):
            rx_as_prescriptionsperson.read()

        # Now assign the RX to themselves
        # (using self.prescriptions_order to do the change as superuser)
        self.prescriptions_order.write({'user_id': self.prescriptions_user2.id})

        # The prescriptionsperson is now able to read it
        rx_as_prescriptionsperson.read()
        # Prescriptionsperson can change a Prescriptions Team of RX
        rx_as_prescriptionsperson.write({'team_id': self.prescriptions_team.id})

        # Prescriptionsperson can't create a RX for other prescriptionsperson
        with self.assertRaises(AccessError):
            self.env['prescriptions.order'].with_user(self.prescriptions_user2).create({
                'partner_id': self.partner.id,
                'user_id': self.prescriptions_user.id
            })

        # Prescriptionsperson can't delete Prescription Orders
        with self.assertRaises(AccessError):
            rx_as_prescriptionsperson.unlink()

        # Prescriptionsperson can confirm the RX
        rx_as_prescriptionsperson.action_confirm()

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_access_portal_user(self):
        """ Test portal user's access rights """
        PrescriptionOrder = self.env['prescriptions.order'].with_user(self.user_portal)
        rx_as_portal_user = PrescriptionOrder.browse(self.prescriptions_order.id)

        # Portal user can see the confirmed RX for which they are assigned as a customer
        with self.assertRaises(AccessError):
            rx_as_portal_user.read()

        self.prescriptions_order.partner_id = self.user_portal.partner_id
        self.prescriptions_order.action_confirm()
        # Portal user can't edit the RX
        with self.assertRaises(AccessError):
            rx_as_portal_user.write({'team_id': self.prescriptions_team.id})
        # Portal user can't create the RX
        with self.assertRaises(AccessError):
            PrescriptionOrder.create({
                'partner_id': self.partner.id,
            })
        # Portal user can't delete the RX which is in 'draft' or 'cancel' state
        self.prescriptions_order.action_cancel()
        with self.assertRaises(AccessError):
            rx_as_portal_user.unlink()

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_access_employee(self):
        """ Test classic employee's access rights """
        PrescriptionOrder = self.env['prescriptions.order'].with_user(self.user_internal)
        rx_as_internal_user = PrescriptionOrder.browse(self.prescriptions_order.id)

        # Employee can't see any RX
        with self.assertRaises(AccessError):
            rx_as_internal_user.read()
        # Employee can't edit the RX
        with self.assertRaises(AccessError):
            rx_as_internal_user.write({'team_id': self.prescriptions_team.id})
        # Employee can't create the RX
        with self.assertRaises(AccessError):
            PrescriptionOrder.create({
                'partner_id': self.partner.id,
            })
        # Employee can't delete the RX
        with self.assertRaises(AccessError):
            rx_as_internal_user.unlink()
