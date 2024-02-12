# -*- coding: utf-8 -*-

from odoo.tests.common import users

from odoo.addons.prescription.tests.common import PrescriptionCommon
from odoo.addons.prescription_team.tests.common import TestPrescriptionCommon


class TestPrescriptionCancel(PrescriptionCommon, TestPrescriptionCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref('prescription.mail_template_prescription_cancellation')
        cls.template.write({
            'subject': 'I can see {{ len(object.partner_id.prescription_ids) }} order(s)',
            'body_html': 'I can see <t t-out="len(object.partner_id.prescription_ids)"/> order(s)',
        })

        cls.partner = cls.env['res.partner'].create({'name': 'foo'})

        cls.manager_order, cls.personnel_order = cls.env['prescription'].create([
            {'partner_id': cls.partner.id, 'user_id': cls.user_prescription_manager.id},
            {'partner_id': cls.partner.id, 'user_id': cls.user_prescription_personnel.id}
        ])
        # Invalidate the cache, e.g. to clear the computation of partner.prescription_ids
        cls.env.invalidate_all()

    @users('user_prescription_personnel')
    def test_personnel_record_rules(self):
        cancel = self.env['prescription.cancel'].create({
            'template_id': self.template.id,
            'order_id': self.personnel_order.id,
        })

        self.assertEqual(cancel.subject, 'I can see 1 order(s)')
        self.assertEqual(cancel.body, 'I can see 1 order(s)')

    @users('user_prescription_manager')
    def test_manager_record_rules(self):
        cancel = self.env['prescription.cancel'].create({
            'template_id': self.template.id,
            'order_id': self.manager_order.id,
        })

        self.assertEqual(cancel.subject, 'I can see 2 order(s)')
        self.assertEqual(cancel.body, 'I can see 2 order(s)')
