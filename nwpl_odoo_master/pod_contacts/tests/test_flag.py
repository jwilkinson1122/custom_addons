from odoo.tests.common import TransactionCase


class TestContactAdministrationFlag(TransactionCase):

    def setUp(self):
        super(TestContactAdministrationFlag, self).setUp()
        self.Flag = self.env["partner.flag"]
        self.Partner = self.env["res.partner"]
        self.FlagCategory = self.env["partner.flag.category"]

    def test_service(self):
        category = self.FlagCategory.create({"name": "Category"})
        partner = self.Patient.create({"name": "Partner"})

        self.assertEqual(partner.partner_flag_count, 0)

        # Create flags
        partner_flag = self.Flag.create(
            {
                "partner_id": partner.id,
                "description": "Description",
                "category_id": category.id,
            }
        )

        # Check partner_flag_count after creating flags
        self.assertEqual(partner.partner_flag_count, 1)

        # Check action_view_flags results
        self.assertEqual(partner.action_view_partner_flags()["res_id"], partner_flag.id)

        # Check if flags are active
        self.assertTrue(partner_flag.active)

        # Check if closure_date is set
        self.assertFalse(partner_flag.closure_date)

        # Close flags
        partner_flag.close()

        # Check if flags are inactive after closing
        self.assertFalse(partner_flag.active)

        # Check if closure_date is set after closing
        self.assertTrue(partner_flag.closure_date)

        # Check display_name of flags
        self.assertEqual(
            partner_flag.display_name,
            "[{}] {}".format(partner_flag.partner_identifier, category.name),
        )
