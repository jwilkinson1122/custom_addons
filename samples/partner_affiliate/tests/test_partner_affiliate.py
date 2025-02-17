from odoo.tests.common import TransactionCase


class TestPartnerAffiliate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_model = self.env["res.partner"]
        self.company = self.partner_model.create(
            {"name": "Test Company", "company_type": "company"}
        )
        self.affiliate = self.partner_model.create(
            {
                "name": "Test Affiliate",
                "company_type": "company",
                "parent_id": self.company.id,
            }
        )

    def test_hierarchy_depth(self):
        child = self.partner_model.create({
            "name": "Child of Affiliate",
            "parent_id": self.affiliate.id,
        })
        hierarchy = self.affiliate._get_children()
        self.assertIn(child, hierarchy)

    def test_partner_affiliate_access_link(self):
        res = self.affiliate.open_affiliate_form()
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["res_model"], "res.partner")
        self.assertEqual(res["res_id"], self.affiliate.id)
        self.assertEqual(res["view_mode"], "form")
        self.assertEqual(res["target"], "current")




class TestPartnerContact(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_model = self.env["res.partner"]
        self.company = self.partner_model.create(
            {"name": "Test Contact", "company_type": "person"}
        )
        self.child = self.partner_model.create(
            {
                "name": "Test Contact",
                "company_type": "person",
                "parent_id": self.company.id,
            }
        )

    def test_partner_contact_access_link(self):
        res = self.child.open_affiliate_form()
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["res_model"], "res.partner")
        self.assertEqual(res["res_id"], self.child.id)
        self.assertEqual(res["view_mode"], "form")
        self.assertEqual(res["target"], "current")
