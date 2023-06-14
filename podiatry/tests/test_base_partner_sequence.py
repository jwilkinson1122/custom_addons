import odoo.tests.common as common


class TestBasePartnerSequence(common.TransactionCase):
    def setUp(self):
        super(TestBasePartnerSequence, self).setUp()

        self.res_partner = self.env["res.partner"]
        self.partner = self.res_partner.create(
            {"name": "test1", "email": "test@test.com"}
        )

    def test_ref_sequence_on_partner(self):
        # Test sequence on creating partner and copying it
        self.assertTrue(self.partner.ref, "A partner has always a ref.")

        copy = self.partner.copy()
        self.assertTrue(
            copy.ref, "A partner with ref created by copy has a ref by default."
        )

    def test_ref_sequence_on_contact(self):
        # Test if sequence doesn't increase on creating a contact child
        contact = self.res_partner.create(
            {
                "name": "contact1",
                "email": "contact@contact.com",
                "parent_id": self.partner.id,
            }
        )
        self.assertEqual(
            self.partner.ref, contact.ref, "All it's ok as sequence doesn't increase."
        )

    def test_unique_ref_on_write(self):
        """Assert that on create or on write, a different ref is assigned"""
        vals = [
            {"name": "test1", "email": "test@test.com"},
            {"name": "test2", "email": "test@test.com"},
        ]
        partners = self.env["res.partner"].create(vals)
        self.assertFalse(partners[0].ref == partners[1].ref)
        partners.write({"ref": False})
        self.assertFalse(partners[0].ref)
        partners.write({})
        self.assertFalse(partners[0].ref == partners[1].ref)
