# Copyright 2022 Creu Blanca

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPodiatryProduct(TransactionCase):
    def setUp(self):
        super(TestPodiatryProduct, self).setUp()

        self.tablet_uom = self.env["uom.uom"].create(
            {
                "name": "Tablets",
                "category_id": self.env.ref("uom.product_uom_categ_unit").id,
                "factor": 1.0,
                "uom_type": "bigger",
                "rounding": 0.001,
            }
        )
        self.tablet_form = self.env["device.form"].create(
            {
                "name": "EFG film coated tablets",
                "uom_ids": [(4, self.tablet_uom.id)],
            }
        )
        self.pod_product_ibuprofen_template = self.env[
            "pod.product.template"
        ].create(
            {
                "name": "Ibuprofen",
                "product_type": "device",
                "ingredients": "Ibuprofen",
                "dosage": "600 mg",
                "form_id": self.tablet_form.id,
            }
        )
        self.pod_product_ibuprofen_30_tablets = self.env[
            "pod.product.product"
        ].create(
            {
                "product_tmpl_id": self.pod_product_ibuprofen_template.id,
                "amount": 30,
                "amount_uom_id": self.tablet_uom.id,
            }
        )

    def test_create_pod_product_without_template(self):
        """
        If a product is created without a selected template,
        the product template should be automatically created
        with the product information.
        """
        pod_product = self.env["pod.product.product"].create(
            {
                "name": "Ibuprofen",
                "product_type": "device",
                "ingredients": "Ibuprofen",
                "dosage": "600 mg",
                "form_id": self.tablet_form.id,
                "amount": 30,
                "amount_uom_id": self.tablet_uom.id,
            }
        )
        pod_product.refresh()
        self.assertTrue(pod_product.product_tmpl_id)
        self.assertEqual(
            pod_product.product_tmpl_id.ingredients,
            pod_product.ingredients,
        )
        self.assertEqual(
            pod_product.product_tmpl_id.name, pod_product.name
        )
        self.assertEqual(
            pod_product.product_tmpl_id.product_type,
            pod_product.product_type,
        )
        self.assertEqual(
            pod_product.product_tmpl_id.dosage, pod_product.dosage
        )
        self.assertEqual(
            pod_product.product_tmpl_id.form_id.id,
            pod_product.form_id.id,
        )
        self.assertEqual(pod_product.product_tmpl_id.product_count, 1)

    def test_create_pod_product_with_template(self):
        """
        If a product is created with a selected template,
        a product template should not be automatically created.
        """
        self.assertTrue(
            self.pod_product_ibuprofen_30_tablets.product_tmpl_id
        )
        self.assertEqual(
            self.pod_product_ibuprofen_30_tablets.product_tmpl_id.ingredients,
            self.pod_product_ibuprofen_template.ingredients,
        )
        self.assertEqual(
            self.pod_product_ibuprofen_30_tablets.product_tmpl_id.name,
            self.pod_product_ibuprofen_template.name,
        )
        self.assertEqual(
            self.pod_product_ibuprofen_30_tablets.product_tmpl_id.product_type,
            self.pod_product_ibuprofen_template.product_type,
        )
        self.assertEqual(
            self.pod_product_ibuprofen_30_tablets.product_tmpl_id.dosage,
            self.pod_product_ibuprofen_template.dosage,
        )
        self.assertEqual(
            self.pod_product_ibuprofen_30_tablets.product_tmpl_id.form_id.id,
            self.pod_product_ibuprofen_template.form_id.id,
        )
        self.assertEqual(
            self.pod_product_ibuprofen_template.product_count, 1
        )

    def test_action_view_pod_product_ids(self):
        action = (
            self.pod_product_ibuprofen_template.action_view_pod_product_ids()
        )
        self.assertEqual(
            action["res_id"], self.pod_product_ibuprofen_30_tablets.id
        )
        self.assertEqual(action["res_model"], "pod.product.product")

    def test_compute_pod_product_name(self):
        self.assertRegex(
            self.pod_product_ibuprofen_template.name_template,
            "Ibuprofen 600 mg EFG film coated tablets",
        )
        self.assertRegex(
            self.pod_product_ibuprofen_30_tablets.name_product,
            "Ibuprofen 600 mg EFG film coated tablets 30.0 Tablets",
        )

    def test_product_check_amount(self):
        """
        If the amount of the product is set to 0, a validation error should raise
        """
        with self.assertRaises(ValidationError):
            self.env["pod.product.product"].create(
                {
                    "name": "Ibuprofen",
                    "product_type": "device",
                    "ingredients": "Ibuprofen",
                    "dosage": "600 mg",
                    "form_id": self.tablet_form.id,
                    "amount": 0,
                    "amount_uom_id": self.tablet_uom.id,
                }
            )

    def test_compute_amount_domain(self):
        pod_device = self.env["pod.product.product"].create(
            {
                "name": "Crutch",
                "product_type": "device",
                "amount": 1,
                "amount_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.assertRegex(
            self.pod_product_ibuprofen_30_tablets.amount_uom_domain,
            "%s" % self.tablet_uom.id,
        )
        self.assertRegex(
            pod_device.amount_uom_domain,
            "%s" % self.env.ref("uom.product_uom_unit").id,
        )

    def test_copy_product(self):
        duplicated_product = self.pod_product_ibuprofen_30_tablets.copy()
        self.assertEqual(
            duplicated_product.product_tmpl_id.id,
            self.pod_product_ibuprofen_template.id,
        )
