# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPodiatrySubPayor(TransactionCase):
    def setUp(self):
        super(TestPodiatrySubPayor, self).setUp()
        self.payor = self.env["res.partner"].create({"name": "Payor", "is_payor": True})

    def test_constrain(self):
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({"name": "Sub Payor", "is_sub_payor": True})
