

from odoo.tests import TransactionCase


class TestRequestGroup(TransactionCase):
    def setUp(self):
        res = super(TestRequestGroup, self).setUp()
        self.patient = self.browse_ref("podiatry_administration.patient_01")
        self.plan = self.browse_ref("podiatry_workflow.basic_check_up")
        return res

    def test_request_workflow(self):
        request = self.env["podiatry.request.group"].create(
            {"patient_id": self.patient.id}
        )
        self.assertNotEqual(request.internal_identifier, "/")
        self.assertTrue(request.is_editable)
        self.assertEqual(request.state, "draft")
        request.draft2active()
        self.assertFalse(request.is_editable)
        self.assertEqual(request.state, "active")
        request.active2suspended()
        self.assertFalse(request.is_editable)
        self.assertEqual(request.state, "suspended")
        request.reactive()
        request.active2error()
        self.assertFalse(request.is_editable)
        self.assertEqual(request.state, "entered-in-error")
        request.reactive()
        request.active2completed()
        self.assertFalse(request.is_editable)
        self.assertEqual(request.state, "completed")
        request.reactive()
        request.cancel()
        self.assertFalse(request.is_editable)
        self.assertEqual(request.state, "cancelled")
