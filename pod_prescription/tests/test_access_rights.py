# -*- coding: utf-8 -*-


from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseUsersCommon
from odoo.addons.pod_prescription.tests.common import PrescriptionCommon


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

        # Create the RX with a specific prescriptionperson
        cls.prescription_order.user_id = cls.prescription_user

    def test_access_prescription_manager(self):
        """ Test prescription manager's access rights """
        PrescriptionOrder = self.env['prescription.order'].with_user(self.prescription_manager)
        rx_as_prescription_manager = PrescriptionOrder.browse(self.prescription_order.id)

        # Manager can see the RX which is assigned to another prescriptionperson
        rx_as_prescription_manager.read()
        # Manager can change a prescriptionperson of the RX
        rx_as_prescription_manager.write({'user_id': self.prescription_user2.id})

        # Manager can create the RX for other prescriptionperson
        prescription_order = PrescriptionOrder.create({
            'partner_id': self.partner.id,
            'user_id': self.prescription_user.id
        })
        self.assertIn(
            prescription_order.id, PrescriptionOrder.search([]).ids,
            'Prescription manager should be able to create the RX of other prescriptionperson')
        # Manager can confirm the RX
        prescription_order.action_confirm()
        # Manager can not delete confirmed RX
        with self.assertRaises(UserError), mute_logger('odoo.models.unlink'):
            prescription_order.unlink()

        # Manager can delete the RX of other prescriptionperson if RX is in 'draft' or 'cancel' state
        rx_as_prescription_manager.unlink()
        self.assertNotIn(
            rx_as_prescription_manager.id, PrescriptionOrder.search([]).ids,
            'Prescription manager should be able to delete the RX')

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_access_prescription_person(self):
        """ Test Prescription Person's access rights """
        PrescriptionOrder = self.env['prescription.order'].with_user(self.prescription_user2)
        rx_as_prescriptionperson = PrescriptionOrder.browse(self.prescription_order.id)

        # Prescriptionperson can see only their own prescription order
        with self.assertRaises(AccessError):
            rx_as_prescriptionperson.read()

        # Now assign the RX to themselves
        # (using self.prescription_order to do the change as superuser)
        self.prescription_order.write({'user_id': self.prescription_user2.id})

        # The prescriptionperson is now able to read it
        rx_as_prescriptionperson.read()
        # Prescriptionperson can change a Prescription Team of RX
        rx_as_prescriptionperson.write({'team_id': self.prescription_team.id})

        # Prescriptionperson can't create a RX for other prescriptionperson
        with self.assertRaises(AccessError):
            self.env['prescription.order'].with_user(self.prescription_user2).create({
                'partner_id': self.partner.id,
                'user_id': self.prescription_user.id
            })

        # Prescriptionperson can't delete Prescription Orders
        with self.assertRaises(AccessError):
            rx_as_prescriptionperson.unlink()

        # Prescriptionperson can confirm the RX
        rx_as_prescriptionperson.action_confirm()

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_access_portal_user(self):
        """ Test portal user's access rights """
        PrescriptionOrder = self.env['prescription.order'].with_user(self.user_portal)
        rx_as_portal_user = PrescriptionOrder.browse(self.prescription_order.id)

        # Portal user can see the confirmed RX for which they are assigned as a customer
        with self.assertRaises(AccessError):
            rx_as_portal_user.read()

        self.prescription_order.partner_id = self.user_portal.partner_id
        self.prescription_order.action_confirm()
        # Portal user can't edit the RX
        with self.assertRaises(AccessError):
            rx_as_portal_user.write({'team_id': self.prescription_team.id})
        # Portal user can't create the RX
        with self.assertRaises(AccessError):
            PrescriptionOrder.create({
                'partner_id': self.partner.id,
            })
        # Portal user can't delete the RX which is in 'draft' or 'cancel' state
        self.prescription_order.action_cancel()
        with self.assertRaises(AccessError):
            rx_as_portal_user.unlink()

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_access_employee(self):
        """ Test classic employee's access rights """
        PrescriptionOrder = self.env['prescription.order'].with_user(self.user_internal)
        rx_as_internal_user = PrescriptionOrder.browse(self.prescription_order.id)

        # Employee can't see any RX
        with self.assertRaises(AccessError):
            rx_as_internal_user.read()
        # Employee can't edit the RX
        with self.assertRaises(AccessError):
            rx_as_internal_user.write({'team_id': self.prescription_team.id})
        # Employee can't create the RX
        with self.assertRaises(AccessError):
            PrescriptionOrder.create({
                'partner_id': self.partner.id,
            })
        # Employee can't delete the RX
        with self.assertRaises(AccessError):
            rx_as_internal_user.unlink()