from datetime import datetime

import freezegun

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestPodiatryProductRequest(TransactionCase):
    def setUp(self):
        super(TestPodiatryProductRequest, self).setUp()
        self.patient = self.env["pod.patient"].create({"name": "Patient"})
        self.encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient.id}
        )
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
        self.oral_administration_route = self.env[
            "pod.administration.route"
        ].create({"name": "Oral"})
        self.ocular_administration_route = self.env[
            "pod.administration.route"
        ].create({"name": "Ocular"})
        self.ibuprofen_template = self.env["pod.product.template"].create(
            {
                "name": "Ibuprofen",
                "product_type": "device",
                "ingredients": "Ibuprofen",
                "dosage": "600 mg",
                "form_id": self.tablet_form.id,
                "administration_route_ids": [
                    (4, self.oral_administration_route.id)
                ],
            }
        )
        self.ibuprofen_30_tablets = self.env["pod.product.product"].create(
            {
                "product_tmpl_id": self.ibuprofen_template.id,
                "amount": 30,
                "amount_uom_id": self.tablet_uom.id,
            }
        )
        self.ibuprofen_60_tablets = self.env["pod.product.product"].create(
            {
                "product_tmpl_id": self.ibuprofen_template.id,
                "amount": 60,
                "amount_uom_id": self.tablet_uom.id,
            }
        )

        self.crutch_template = self.env["pod.product.template"].create(
            {
                "name": "crutch",
                "product_type": "device",
            }
        )
        self.pod_product_crutch = self.env[
            "pod.product.product"
        ].create(
            {
                "product_tmpl_id": self.crutch_template.id,
                "amount": 1,
                "amount_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        self.ml_uom = self.env["uom.uom"].create(
            {
                "name": "ml",
                "category_id": self.env.ref("uom.product_uom_categ_vol").id,
                "factor": 1000,
                "uom_type": "smaller",
                "rounding": 0.001,
            }
        )

        self.drops_uom = self.env["uom.uom"].create(
            {
                "name": "Drops",
                "category_id": self.env.ref("uom.product_uom_categ_vol").id,
                "factor": 20000,
                "uom_type": "smaller",
                "rounding": 0.001,
            }
        )
        self.solution_form = self.env["device.form"].create(
            {
                "name": "Eye drops in solution",
                "uom_ids": [(4, self.drops_uom.id), (4, self.ml_uom.id)],
            }
        )

        self.acular_template = self.env["pod.product.template"].create(
            {
                "name": "Acular",
                "product_type": "device",
                "ingredients": "Ketorolac tromethamol",
                "dosage": "5 mg/ml",
                "form_id": self.solution_form.id,
                "administration_route_ids": [
                    (4, self.ocular_administration_route.id)
                ],
            }
        )
        self.acular_5_ml = self.env["pod.product.product"].create(
            {
                "product_tmpl_id": self.acular_template.id,
                "amount": 5,
                "amount_uom_id": self.ml_uom.id,
            }
        )
        self.acular_10_ml = self.env["pod.product.product"].create(
            {
                "product_tmpl_id": self.acular_template.id,
                "amount": 10,
                "amount_uom_id": self.ml_uom.id,
            }
        )
        self.internal_request = self.env["pod.product.request"].create(
            {
                "pod_product_template_id": self.ibuprofen_template.id,
                "category": "inpatient",
                "patient_id": self.patient.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 60,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
                "administration_route_id": self.oral_administration_route.id,
            }
        )
        self.external_request = self.env["pod.product.request"].create(
            {
                "pod_product_template_id": self.ibuprofen_template.id,
                "category": "discharge",
                "patient_id": self.patient.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 1,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 30,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )

    def test_compute_fields_from_request_order_id(self):
        # Compute the fields if the request comes from a request_order
        request_order = self.env["pod.product.request.order"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "category": "discharge",
            }
        )
        product_request = self.env["pod.product.request"].create(
            {
                "request_order_id": request_order.id,
                "pod_product_template_id": self.ibuprofen_template.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 60,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )
        self.assertEqual(
            request_order.patient_id.id, product_request.patient_id.id
        )
        self.assertEqual(
            request_order.encounter_id.id, product_request.encounter_id.id
        )
        self.assertEqual(request_order.category, product_request.category)

        # Compute the fields if the request does not come from a request_order
        product_request_2 = self.env["pod.product.request"].create(
            {
                "pod_product_template_id": self.ibuprofen_template.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 60,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )
        product_request_2.with_context(
            {"default_patient_id": self.patient.id}
        )._compute_patient_id_from_request_order_id()
        self.assertEqual(product_request_2.patient_id.id, self.patient.id)
        self.assertEqual(product_request_2.encounter_id.id, self.encounter.id)
        product_request_2.with_context(
            {"default_category": "discharge"}
        )._compute_category_from_request_order_id()
        self.assertEqual(product_request_2.category, "discharge")

        # Compute the fields if it does not have patient or category
        product_request_3 = self.env["pod.product.request"].create(
            {
                "pod_product_template_id": self.ibuprofen_template.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 60,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )
        self.assertFalse(product_request_3.patient_id)
        self.assertFalse(product_request_3.encounter_id)
        self.assertFalse(product_request_3.category)

    def test_get_default_dose_uom_id(self):
        with Form(self.internal_request) as request:
            request.pod_product_template_id = self.acular_template
            self.assertEqual(request.dose_uom_id.id, self.drops_uom.id)
            request.pod_product_template_id = self.crutch_template
            self.assertEqual(
                request.dose_uom_id.id, self.env.ref("uom.product_uom_unit").id
            )

    def test_get_default_administration_route_id(self):
        with Form(self.internal_request) as request:
            request.pod_product_template_id = self.acular_template
            self.assertEqual(
                request.administration_route_id.id,
                self.ocular_administration_route.id,
            )
            request.pod_product_template_id = self.crutch_template
            self.assertEqual(request.administration_route_id.id, False)

    def test_create_internal_request(self):
        self.assertEqual(self.patient.id, self.internal_request.patient_id.id)
        self.assertFalse(self.internal_request.pod_product_id)
        self.assertEqual(self.internal_request.quantity_to_dispense, 0)

    def test_validate_internal_request(self):
        with freezegun.freeze_time("2022-01-01"):
            self.internal_request.validate_action()
        self.assertEqual(self.internal_request.state, "active")
        self.assertEqual(
            self.internal_request.requester_id.id, self.env.user.id
        )
        self.assertEqual(
            self.internal_request.validation_date,
            datetime(2022, 1, 1, 0, 0, 0),
        )

    def test_create_external_request_of_device(self):
        request = self.env["pod.product.request"].create(
            {
                "pod_product_template_id": self.crutch_template.id,
                "category": "discharge",
                "patient_id": self.patient.id,
                "dose_quantity": 1,
                "dose_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.assertEqual(
            request.pod_product_id.id, self.pod_product_crutch.id
        )
        self.assertEqual(request.quantity_to_dispense, 1)

    def test_create_external_request_of_device_tablet(self):
        """
        In this case the dose unit and the amount unit
        of the pod product are the same
        """
        request = self.external_request
        self.assertEqual(
            request.pod_product_id.id,
            self.ibuprofen_30_tablets.id,
        )
        self.assertEqual(request.quantity_to_dispense, 1)
        request.duration = 40
        self.assertEqual(
            request.pod_product_id.id,
            self.ibuprofen_60_tablets.id,
        )
        self.assertEqual(request.quantity_to_dispense, 1)
        request.duration = 80
        self.assertEqual(
            request.pod_product_id.id,
            self.ibuprofen_60_tablets.id,
        )
        self.assertEqual(request.quantity_to_dispense, 2)

    def test_create_external_request_of_device_solution(self):
        """
        In this case the dose unit and the amount unit
        of the pod product are different
        """
        request = self.env["pod.product.request"].create(
            {
                "pod_product_template_id": self.acular_template.id,
                "category": "discharge",
                "patient_id": self.patient.id,
                "dose_quantity": 3,
                "dose_uom_id": self.drops_uom.id,
                "rate_quantity": 2,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 10,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )

        # We consider that a drop is equal to 0,05 ml
        # total_dose = 3 drops * 0,05 ml/ 1 drop *  2 drops/day * 10 days = 3 ml
        self.assertEqual(request.pod_product_id.id, self.acular_5_ml.id)
        self.assertEqual(request.quantity_to_dispense, 1)
        request.duration = 30
        # total_dose = 3 drops * 0,05 ml/ 1 drop *  2 drops/day * 30 days = 9 ml
        self.assertEqual(request.pod_product_id.id, self.acular_10_ml.id)
        self.assertEqual(request.quantity_to_dispense, 1)
        request.duration = 100
        # total_dose = 3 drops * 0,05 ml/ 1 drop *  2 drops/day * 100 days = 30 ml
        self.assertEqual(request.pod_product_id.id, self.acular_10_ml.id)
        self.assertEqual(request.quantity_to_dispense, 3)

    def test_validate_external_request(self):
        with freezegun.freeze_time("2022-01-01"):
            self.external_request.validate_action()
        self.assertEqual(self.external_request.state, "completed")
        self.assertEqual(
            self.external_request.requester_id.id, self.env.user.id
        )
        self.assertEqual(
            self.external_request.validation_date,
            datetime(2022, 1, 1, 0, 0, 0),
        )

    def test_create_pod_product_administration(self):
        self.assertEqual(
            self.internal_request.product_administrations_count, 0
        )
        self.internal_request.validate_action()
        action = self.internal_request.create_pod_product_administration()
        self.assertEqual(
            action["context"]["default_pod_product_template_id"],
            self.ibuprofen_template.id,
        )
        self.assertEqual(action["context"]["default_quantity_administered"], 1)
        self.assertEqual(
            action["context"]["default_quantity_administered_uom_id"],
            self.tablet_uom.id,
        )
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )

    def test_cancel_external_request(self):
        self.assertEqual(self.external_request.state, "draft")
        with freezegun.freeze_time("2022-01-01"):
            self.external_request.cancel_action()
        self.assertEqual(self.external_request.state, "cancelled")
        self.assertEqual(
            self.external_request.cancel_user_id.id, self.env.user.id
        )
        self.assertEqual(
            self.external_request.cancel_date, datetime(2022, 1, 1, 0, 0, 0)
        )

    def test_cancel_internal_request_without_administrations(self):
        self.assertEqual(self.internal_request.state, "draft")
        with freezegun.freeze_time("2022-01-01"):
            self.internal_request.cancel_action()
        self.assertEqual(self.internal_request.state, "cancelled")
        self.assertEqual(
            self.internal_request.cancel_user_id.id, self.env.user.id
        )
        self.assertEqual(
            self.internal_request.cancel_date, datetime(2022, 1, 1, 0, 0, 0)
        )

    def test_cancel_internal_request_with_administrations(self):
        self.assertEqual(self.internal_request.state, "draft")
        self.internal_request.validate_action()
        administration = self.env["pod.product.administration"].create(
            {
                "product_request_id": self.internal_request.id,
                "quantity_administered": 1,
                "pod_product_template_id": self.ibuprofen_template.id,
                "quantity_administered_uom_id": self.tablet_uom.id,
            }
        )
        administration.complete_administration_action()
        self.assertEqual(
            self.internal_request.product_administrations_count, 1
        )
        with self.assertRaises(ValidationError):
            self.internal_request.cancel_action()
        administration.cancel_action()
        self.assertEqual(
            self.internal_request.product_administrations_count, 0
        )
        self.internal_request.cancel_action()
        self.assertEqual(self.internal_request.state, "cancelled")

    def test_action_view_pod_product_administration(self):
        administration = self.env["pod.product.administration"].create(
            {
                "product_request_id": self.internal_request.id,
                "quantity_administered": 1,
                "pod_product_template_id": self.ibuprofen_template.id,
                "quantity_administered_uom_id": self.tablet_uom.id,
            }
        )
        administration.complete_administration_action()
        self.internal_request.refresh()
        self.internal_request.flush()
        action = (
            self.internal_request.action_view_pod_product_administration()
        )
        self.assertEqual(action["res_id"], administration.id)

    def test_product_request_constrains(self):
        with self.assertRaises(ValidationError):
            self.internal_request.dose_quantity = 0
        with self.assertRaises(ValidationError):
            self.internal_request.rate_quantity = 0
        with self.assertRaises(ValidationError):
            self.internal_request.duration = 0
