# -*- coding: utf-8 -*-

from odoo.tests.common import users

from odoo.addons.pod_prescription.tests.common import PrescriptionCommon
from odoo.addons.pod_prescription_team.tests.common import TestPrescriptionCommon


class TestPrescriptionOrderCancel(PrescriptionCommon, TestPrescriptionCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref('pod_prescription.mail_template_prescription_cancellation')
        cls.template.write({
            'subject': 'I can see {{ len(object.partner_id.prescription_order_ids) }} order(s)',
            'body_html': 'I can see <t t-out="len(object.partner_id.prescription_order_ids)"/> order(s)',
        })

        cls.partner = cls.env['res.partner'].create({'name': 'foo'})

        cls.manager_order, cls.personnel_order = cls.env['prescription.order'].create([
            {'partner_id': cls.partner.id, 'user_id': cls.user_prescription_manager.id},
            {'partner_id': cls.partner.id, 'user_id': cls.user_prescription_personnel.id}
        ])
        # Invalidate the cache, e.g. to clear the computation of partner.prescription_order_ids
        cls.env.invalidate_all()

    @users('user_prescription_personnel')
    def test_personnel_record_rules(self):
        cancel = self.env['prescription.order.cancel'].create({
            'template_id': self.template.id,
            'order_id': self.personnel_order.id,
        })

        self.assertEqual(cancel.subject, 'I can see 1 order(s)')
        self.assertEqual(cancel.body, 'I can see 1 order(s)')

    @users('user_prescription_manager')
    def test_manager_record_rules(self):
        cancel = self.env['prescription.order.cancel'].create({
            'template_id': self.template.id,
            'order_id': self.manager_order.id,
        })

        self.assertEqual(cancel.subject, 'I can see 2 order(s)')
        self.assertEqual(cancel.body, 'I can see 2 order(s)')
