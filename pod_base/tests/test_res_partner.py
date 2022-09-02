
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()
        self.partner_1 = self.env.ref(
            'pod.res_partner_patient_1'
        )
        self.patient_1 = self.env.ref(
            'pod.pod.patient_patient_1'
        )

    def test_get_pod_entity(self):
        """ Test returns correct pod entity """
        self.partner_1.type = 'pod.patient'
        res = self.partner_1._get_pod_entity()
        self.assertEquals(
            res.partner_id,
            self.partner_1,
        )

    def test_get_pod_entity_no_type(self):
        """ Test returns nothing if no type """
        self.partner_1.type = None
        self.assertFalse(
            self.partner_1._get_pod_entity(),
        )

    def test_get_pod_entity_not_pod(self):
        """ Test returns nothing if not pod type """
        self.partner_1.type = 'invoice'
        self.assertFalse(
            self.partner_1._get_pod_entity(),
        )
