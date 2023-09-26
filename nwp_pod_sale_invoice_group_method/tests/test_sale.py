from odoo.addons.nwp_pod_careplan_sale.tests import common


class TestNWPSale(common.PodiatrySavePointCase):
    def test_careplan_sale(self):
        encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient_01.id, "practice_id": self.practice.id}
        )
        encounter_02 = self.env["pod.encounter"].create(
            {"patient_id": self.patient_01.id, "practice_id": self.practice.id}
        )
        careplan = self.env["pod.careplan"].new(
            {
                "patient_id": self.patient_01.id,
                "encounter_id": encounter.id,
                "coverage_id": self.coverage_01.id,
                "sub_payor_id": self.sub_payor.id,
            }
        )
        careplan._onchange_encounter()
        careplan = careplan.create(careplan._convert_to_write(careplan._cache))
        self.assertEqual(careplan.practice_id, encounter.practice_id)
        wizard = self.env["pod.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line.id,
            }
        )
        self.action.is_billable = False
        wizard.run()
        groups = self.env["pod.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertTrue(groups)
        device_requests = self.env["pod.device.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertEqual(careplan.state, "draft")
        self.assertFalse(device_requests.filtered(lambda r: r.is_billable))
        self.assertTrue(
            groups.filtered(lambda r: r.child_model == "pod.device.request")
        )
        self.assertTrue(
            groups.filtered(
                lambda r: (r.is_sellable_insurance or r.is_sellable_private)
                and r.child_model == "pod.device.request"
            )
        )
        self.assertTrue(
            groups.filtered(
                lambda r: r.is_billable
                and r.child_model == "pod.device.request"
            )
        )
        encounter.create_sale_order()
        self.assertTrue(encounter.sale_order_ids)

        procedure_requests = self.env["pod.procedure.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertGreater(len(procedure_requests), 0)
        device_requests = self.env["pod.device.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertGreater(len(device_requests), 0)
        procedure_requests = self.env["pod.procedure.request"].search(
            [("careplan_id", "=", careplan.id)]
        )
        self.assertGreater(len(procedure_requests), 0)
        for group in careplan.request_group_ids:
            self.assertEqual(group.state, "completed")
        self.assertTrue(encounter.sale_order_ids)
        for sale_order in encounter.sale_order_ids:
            self.assertTrue(sale_order.patient_name)
            original_patient_name = sale_order.patient_name
            patient_name = "{} {}".format(original_patient_name, "TEST")
            sale_order.patient_name = patient_name
            for line in sale_order.order_line:
                self.assertTrue(line.tax_id)
                self.assertEqual(line.patient_name, patient_name)
        preinvoice_obj = self.env["sale.preinvoice.group"]
        self.assertFalse(
            preinvoice_obj.search([("agreement_id", "=", self.agreement.id)])
        )
        self.env["wizard.sale.preinvoice.group"].create(
            {
                "company_ids": [(6, 0, self.company.ids)],
                "payor_ids": [(6, 0, self.payor.ids)],
            }
        ).run()
        self.assertFalse(
            preinvoice_obj.search([("agreement_id", "=", self.agreement.id)])
        )
        self.assertTrue(encounter.sale_order_ids)
        for sale_order in encounter.sale_order_ids:
            sale_order.action_confirm()
            self.assertIn(sale_order.state, ["done", "sale"])
            for line in sale_order.order_line:
                line.qty_delivered = line.product_uom_qty
        self.assertTrue(
            encounter.sale_order_ids.filtered(
                lambda r: r.preinvoice_status == "to preinvoice"
                and any(
                    line.invoice_group_method_id
                    == self.browse_ref("nwp_pod_careplan_sale.by_preinvoicing")
                    for line in r.order_line
                )
            )
        )
        self.env["wizard.sale.preinvoice.group"].create(
            {
                "company_ids": [(6, 0, self.company.ids)],
                "payor_ids": [(6, 0, self.payor.ids)],
            }
        ).run()
        preinvoices = preinvoice_obj.search(
            [("agreement_id", "=", self.agreement.id), ("state", "=", "draft")]
        )
        self.assertTrue(preinvoices)
        # Test cancellation of preinvoices
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.cancel()
            self.assertFalse(preinvoice.line_ids)
        preinvoices = preinvoice_obj.search(
            [("agreement_id", "=", self.agreement.id), ("state", "=", "draft")]
        )
        self.assertFalse(preinvoices)
        self.env["wizard.sale.preinvoice.group"].create(
            {
                "company_ids": [(6, 0, self.company.ids)],
                "payor_ids": [(6, 0, self.payor.ids)],
            }
        ).run()
        preinvoices = preinvoice_obj.search(
            [("agreement_id", "=", self.agreement.id), ("state", "=", "draft")]
        )
        self.assertTrue(preinvoices)
        # Test unlink of not validated order_lines
        for preinvoice in preinvoices:
            self.assertTrue(preinvoice.non_validated_line_ids)
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            preinvoice.close_sorting()
            self.assertTrue(preinvoice.non_validated_line_ids)
            preinvoice.close()
            self.assertFalse(preinvoice.non_validated_line_ids)
        preinvoices = preinvoice_obj.search(
            [("agreement_id", "=", self.agreement.id), ("state", "=", "draft")]
        )
        self.assertFalse(preinvoices)
        self.env["wizard.sale.preinvoice.group"].create(
            {
                "company_ids": [(6, 0, self.company.ids)],
                "payor_ids": [(6, 0, self.payor.ids)],
            }
        ).run()
        preinvoices = preinvoice_obj.search(
            [("agreement_id", "=", self.agreement.id), ("state", "=", "draft")]
        )
        self.assertTrue(preinvoices)
        invoice_obj = self.env["account.move"]
        self.assertFalse(invoice_obj.search([("partner_id", "=", self.payor.id)]))
        # Test barcodes
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()

            result = preinvoice.scan_barcode_preinvoice(encounter.internal_identifier)
            self.assertEqual(result["context"]["default_state"], "waiting")
            result = preinvoice.scan_barcode_preinvoice("No Barcode")
            self.assertEqual(result["context"]["default_state"], "warning")
            result = preinvoice.scan_barcode_preinvoice(
                encounter_02.internal_identifier
            )
            self.assertEqual(result["context"]["default_state"], "warning")
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.move_id)
        invoices = invoice_obj.search(
            [("partner_id", "in", [self.payor.id, self.sub_payor.id])]
        )
        self.assertTrue(invoices)
        # Test invoice unlink
        for invoice in invoices:
            self.assertEqual(invoice.state, "draft")
            invoice.line_ids.unlink()
        for sale_order in encounter.sale_order_ids:
            for line in sale_order.order_line:
                self.assertFalse(line.preinvoice_group_id)
        # Test manual validation of lines on preinvoices
        preinvoices = preinvoice_obj.search(
            [("agreement_id", "=", self.agreement.id), ("state", "=", "draft")]
        )
        self.assertFalse(preinvoices)
        self.env["wizard.sale.preinvoice.group"].create(
            {
                "company_ids": [(6, 0, self.company.ids)],
                "payor_ids": [(6, 0, self.payor.ids)],
            }
        ).run()
        preinvoices = preinvoice_obj.search(
            [("agreement_id", "=", self.agreement.id), ("state", "=", "draft")]
        )
        self.assertTrue(preinvoices)
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            for line in preinvoice.line_ids:
                line.validate_line()
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.line_ids)
            self.assertTrue(preinvoice.move_id)
        invoices = invoice_obj.search(
            [
                ("partner_id", "in", [self.payor.id, self.sub_payor.id]),
                ("state", "=", "draft"),
            ]
        )
        self.assertTrue(invoices)
        # Invoices should be reused
        self.assertEqual(1, len(invoices))
