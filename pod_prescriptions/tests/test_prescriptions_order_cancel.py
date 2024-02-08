# -*- coding: utf-8 -*-

from odoo.tests.common import users

from odoo.addons.pod_prescriptions.tests.common import PrescriptionCommon
from odoo.addons.pod_prescriptions_team.tests.common import TestPrescriptionsCommon


class TestPrescriptionOrderCancel(PrescriptionCommon, TestPrescriptionsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref('pod_prescriptions.mail_template_prescriptions_cancellation')
        cls.template.write({
            'subject': 'I can see {{ len(object.partner_id.prescriptions_order_ids) }} order(s)',
            'body_html': 'I can see <t t-out="len(object.partner_id.prescriptions_order_ids)"/> order(s)',
        })

        cls.partner = cls.env['res.partner'].create({'name': 'foo'})

        cls.manager_order, cls.prescriptionsman_order = cls.env['prescriptions.order'].create([
            {'partner_id': cls.partner.id, 'user_id': cls.user_prescriptions_manager.id},
            {'partner_id': cls.partner.id, 'user_id': cls.user_prescriptions_prescriptionsman.id}
        ])
        # Invalidate the cache, e.g. to clear the computation of partner.prescriptions_order_ids
        cls.env.invalidate_all()

    @users('user_prescriptions_prescriptionsman')
    def test_prescriptionsman_record_rules(self):
        cancel = self.env['prescriptions.order.cancel'].create({
            'template_id': self.template.id,
            'order_id': self.prescriptionsman_order.id,
        })

        self.assertEqual(cancel.subject, 'I can see 1 order(s)')
        self.assertEqual(cancel.body, 'I can see 1 order(s)')

    @users('user_prescriptions_manager')
    def test_manager_record_rules(self):
        cancel = self.env['prescriptions.order.cancel'].create({
            'template_id': self.template.id,
            'order_id': self.manager_order.id,
        })

        self.assertEqual(cancel.subject, 'I can see 2 order(s)')
        self.assertEqual(cancel.body, 'I can see 2 order(s)')
