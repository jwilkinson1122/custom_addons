from odoo.tests.common import TransactionCase, SavepointCase
from odoo.api import Environment


class TestPartnerAffiliate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up shared environment and admin user
        cls.admin = cls.env.ref("base.user_root")
        cls.env = Environment(cls.env.cr, cls.admin.id, {})

        # Create partners and hierarchy for SavepointCase
        cls.partner_model = cls.env["res.partner"]
        cls.company = cls.partner_model.create({"name": "Parent", "is_company": True})
        cls.company2 = cls.partner_model.create({"name": "Parent2", "is_company": True})
        cls.company_contact = cls.partner_model.create(
            {"name": "Company Contact", "type": "contact", "parent_id": cls.company.id}
        )
        cls.affiliate = cls.partner_model.create(
            {"name": "Affiliate", "is_company": True, "parent_id": cls.company.id}
        )
        cls.affiliate_contact = cls.partner_model.create(
            {"name": "Contact", "type": "contact", "parent_id": cls.affiliate.id}
        )

    def setUp(self):
        super().setUp()
        # Create partners for TransactionCase-specific tests
        self.transaction_partner_model = self.env["res.partner"]
        self.transaction_company = self.transaction_partner_model.create(
            {"name": "Test Company", "company_type": "company"}
        )
        self.transaction_affiliate = self.transaction_partner_model.create(
            {
                "name": "Test Affiliate",
                "company_type": "company",
                "parent_id": self.transaction_company.id,
            }
        )

    # Tests from the TransactionCase
    def test_partner_affiliate_access_link(self):
        res = self.transaction_affiliate.open_affiliate_form()
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["res_model"], "res.partner")
        self.assertEqual(res["res_id"], self.transaction_affiliate.id)
        self.assertEqual(res["view_mode"], "form")
        self.assertEqual(res["target"], "current")

    # Tests from the SavepointCase
    def test_company_is_company_parent(self):
        assert self.company.is_company_parent == 1

    def test_affiliate_is_not_company_parent(self):
        assert self.affiliate.is_company_parent == 0

    def test_company_contact_parent_id(self):
        assert self.affiliate.highest_parent_id.id == self.company.id

    def test_affiliate_contact_parent_id(self):
        assert self.affiliate_contact.highest_parent_id.id == self.company.id

    def test_change_affiliate_parent_id(self):
        self.affiliate.parent_id = self.company2.id
        self.env["res.partner"].sudo().compute_all_top_parent_id()
        assert self.affiliate_contact.highest_parent_id.id == self.company2.id
