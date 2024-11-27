from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.tests import common
from odoo.tests.common import SavepointCase, TransactionCase
from ..models.res_partner import INVOICE


class TestResPartnerDOB(common.TransactionCase):
    def setUp(self):
        super(TestResPartnerDOB, self).setUp()
        self.partner_admin = self.env.ref("base.partner_admin")
        self.partner_admin.write({"birthdate_date": "1991-09-05"})

    def test_compute_age(self):
        self.partner_admin._compute_age()
        age = relativedelta(
            fields.Date.today(), self.partner_admin.birthdate_date
        ).years
        self.assertEqual(self.partner_admin.age, age)


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parent = cls.env["res.partner"].create(
            {
                "name": "Parent",
                "is_company": True,
            }
        )
        cls.parent_address = cls.env["res.partner"].create(
            {
                "name": "Invoicing Address",
                "type": INVOICE,
                "parent_id": cls.parent.id,
            }
        )
        cls.affiliate = cls.env["res.partner"].create(
            {
                "name": "Affiliate",
                "is_company": True,
                "parent_id": cls.parent.id,
            }
        )
        cls.affiliate_contact = cls.env["res.partner"].create(
            {
                "name": "Contact",
                "type": "contact",
                "parent_id": cls.affiliate.id,
            }
        )

    def test_box_not_checked(self):
        assert self.affiliate.address_get([INVOICE])[INVOICE] == self.affiliate.id

    def test_box_checked(self):
        self.affiliate.use_parent_invoice_address = True
        assert self.affiliate.address_get([INVOICE])[INVOICE] == self.parent_address.id

    def test_invoice_address_not_asked(self):
        self.affiliate.use_parent_invoice_address = True
        res = self.affiliate.address_get()
        assert INVOICE not in res

    def test_contact_of_affiliate(self):
        self.affiliate.use_parent_invoice_address = True
        assert (
            self.affiliate_contact.address_get([INVOICE])[INVOICE]
            == self.parent_address.id
        )


class TestBasePartnerTwoLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner_model = cls.env["res.partner"].with_context(
            _two_lines_partner_address=True
        )
        partner = partner_model.create(
            {"name": "Test Company Name", "company_type": "company"}
        )
        cls.child_partner_name = partner_model.create(
            {
                "name": "Test Partner Name",
                "type": "invoice",
                "parent_id": partner.id,
            }
        )
        cls.child_partner_no_name = partner_model.create(
            {
                "name": "",
                "type": "invoice",
                "parent_id": partner.id,
            }
        )

        partner_2 = partner_model.create(
            {"name": "Test Company, LTD", "company_type": "company"}
        )

        cls.child_partner_name_2 = partner_model.create(
            {
                "name": "Test Partner Name 2",
                "type": "invoice",
                "parent_id": partner_2.id,
            }
        )

    def test_get_name(self):
        # Partner with name.
        self.assertEqual(
            self.child_partner_name.display_name, "Test Company Name\nTest Partner Name"
        )

        self.assertEqual(
            self.child_partner_name_2.display_name,
            "Test Company, LTD\nTest Partner Name 2",
        )

        # Partner without a name.
        self.assertEqual(
            self.child_partner_no_name.display_name,
            "Test Company Name, Invoice Address",
        )
        self.assertEqual(
            self.child_partner_no_name.with_context(
                _keep_partner_address_type=True
            ).display_name,
            "Test Company Name\nInvoice Address",
        )
