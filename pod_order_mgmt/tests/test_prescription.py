from odoo.addons.product_configurator.tests import (
    test_product_configurator_test_cases as TC,
)


class Prescription(TC.ProductConfiguratorTestCases):
    def setUp(self):
        super(Prescription, self).setUp()
        self.PrescriptionId = self.env["pod.prescription.order"]
        self.productPricelist = self.env["product.pricelist"]
        self.resPartner = self.env.ref("pod_order_mgmt.partner_prescription_1")
        self.currency_id = self.env.ref("base.USD")
        self.ProductConfWizard = self.env["product.configurator.prescription"]

    def test_00_reconfigure_product(self):
        pricelist_id = self.productPricelist.create(
            {
                "name": "Test Pricelist",
                "currency_id": self.currency_id.id,
            }
        )
        prescription_order_id = self.PrescriptionId.create(
            {
                "partner_id": self.resPartner.id,
                "partner_invoice_id": self.resPartner.id,
                "partner_shipping_id": self.resPartner.id,
                "pricelist_id": pricelist_id.id,
            }
        )
        context = dict(
            default_order_id=prescription_order_id.id,
            wizard_model="product.configurator.prescription",
        )

        self.ProductConfWizard = self.env["product.configurator.prescription"].with_context(
            **context
        )
        prescription_order_id.action_config_start()
        self._configure_product_nxt_step()
        prescription_order_id.prescription_order_lines.reconfigure_product()
        product_tmpl = prescription_order_id.prescription_order_lines.product_id.product_tmpl_id
        self.assertEqual(
            product_tmpl.id,
            self.config_product.id,
            "Error: If product_tmpl not exists" " Method: action_config_start()",
        )
