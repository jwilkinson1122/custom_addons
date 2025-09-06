from odoo.tests.common import TransactionCase


class TestContactAdministrationFlag(TransactionCase):

    def setUp(self):
        super(TestContactAdministrationFlag, self).setUp()
        self.Flag = self.env["res.partner.flag"]
        self.Partner = self.env["res.partner"]
        self.FlagCategory = self.env["res.partner.flag.category"]

    def test_service(self):
        category = self.FlagCategory.create({"name": "Category"})
        partner = self.Patient.create({"name": "Partner"})

        self.assertEqual(partner.res_partner_flag_count, 0)

        # Create flags
        res_partner_flag = self.Flag.create(
            {
                "partner_id": partner.id,
                "description": "Description",
                "category_id": category.id,
            }
        )

        # Check res_partner_flag_count after creating flags
        self.assertEqual(partner.res_partner_flag_count, 1)

        # Check action_view_flags results
        self.assertEqual(
            partner.action_view_res_partner_flags()["res_id"], res_partner_flag.id
        )

        # Check if flags are active
        self.assertTrue(res_partner_flag.active)

        # Check if closure_date is set
        self.assertFalse(res_partner_flag.closure_date)

        # Close flags
        res_partner_flag.close()

        # Check if flags are inactive after closing
        self.assertFalse(res_partner_flag.active)

        # Check if closure_date is set after closing
        self.assertTrue(res_partner_flag.closure_date)

        # Check display_name of flags
        self.assertEqual(
            res_partner_flag.display_name,
            "[{}] {}".format(res_partner_flag.partner_identifier, category.name),
        )
