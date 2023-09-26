from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSequence(TransactionCase):
    def setUp(self):
        super().setUp()
        self.patient = self.env["pod.patient"].create({"name": "Patient"})
        self.practice = self.env["res.partner"].create(
            {
                "name": "Practice",
                "is_pod": True,
                "is_practice": True,
                "encounter_sequence_prefix": "S",
            }
        )
        self.encounter = self.env["pod.encounter"].create(
            {"patient_id": self.patient.id, "practice_id": self.practice.id}
        )
        self.product = self.env["product.product"].create(
            {"name": "Product", "type": "consu"}
        )
        self.uom_unit = self.env.ref("uom.product_uom_unit")

    def check_model(self, model, vals):
        values = vals.copy()
        values.update(patient_id=self.patient.id)
        request_1 = self.env[model].create(values)
        self.assertNotEqual(
            request_1.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        values = vals.copy()
        values.update(patient_id=self.patient.id, encounter_id=self.encounter.id)
        request_2 = self.env[model].create(values)
        self.assertEqual(
            request_2.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        values = vals.copy()
        values.update(patient_id=self.patient.id)
        request_3 = (
            self.env[model]
            .with_context(default_encounter_id=self.encounter.id)
            .create(values)
        )
        self.assertEqual(
            request_3.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        return request_1, request_2, request_3

    def test_careplan(self):
        self.check_model("pod.careplan", {})

    def test_procedure(self):
        self.check_model("pod.procedure", {})

    def test_procedure_request(self):
        request_1, request_2, request_3 = self.check_model(
            "pod.procedure.request", {}
        )
        event_1 = request_1.generate_event()
        self.assertFalse(event_1.encounter_id)
        self.assertNotEqual(
            event_1.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        event_2 = request_2.generate_event()
        self.assertTrue(event_2.encounter_id)
        self.assertEqual(
            event_2.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        event_3 = request_3.generate_event()
        self.assertTrue(event_3.encounter_id)
        self.assertEqual(
            event_3.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )

    def test_request_group(self):
        self.check_model("pod.request.group", {})

    def test_laboratory_event(self):
        request = self.env["pod.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        self.check_model(
            "pod.laboratory.event",
            {
                "patient_id": self.patient.id,
                "laboratory_request_id": request.id,
            },
        )

    def test_laboratory_request(self):
        request = self.env["pod.laboratory.request"].create(
            {"patient_id": self.patient.id}
        )
        self.check_model(
            "pod.laboratory.request",
            {
                "patient_id": self.patient.id,
                "laboratory_request_id": request.id,
            },
        )

    def test_device_administration(self):
        self.check_model(
            "pod.device.administration",
            {
                "product_id": self.product.id,
                "product_uom_id": self.uom_unit.id,
            },
        )

    def test_device_request(self):
        request_1, request_2, request_3 = self.check_model(
            "pod.device.request",
            {
                "product_id": self.product.id,
                "product_uom_id": self.uom_unit.id,
            },
        )
        event_1 = request_1.generate_event()
        self.assertFalse(event_1.encounter_id)
        self.assertNotEqual(
            event_1.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        event_2 = request_2.generate_event()
        self.assertTrue(event_2.encounter_id)
        self.assertEqual(
            event_2.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )
        event_3 = request_3.generate_event()
        self.assertTrue(event_3.encounter_id)
        self.assertEqual(
            event_3.internal_identifier[: len(self.encounter.internal_identifier)],
            self.encounter.internal_identifier,
        )

    def test_document_reference(self):
        document_type = self.env["pod.document.type"].create(
            {
                "name": "CI",
                "report_action_id": self.browse_ref(
                    "pod_document.action_report_document_report_base"
                ).id,
            }
        )
        self.env["pod.document.type.lang"].create(
            {
                "lang": "en_US",
                "document_type_id": document_type.id,
                "text": "<p>I, ${object.patient_id.name}, recognize the protocol"
                " ${object.name} and sign this document.</p>"
                "<p>Signed:${object.patient_id.name}<br></p>",
            }
        )
        document_type.post()
        self.check_model(
            "pod.document.reference",
            {"document_type_id": document_type.id},
        )

    def test_diagnostic_report(self):
        self.check_model("pod.diagnostic.report", {})

    def test_encounter(self):
        with self.assertRaises(ValidationError):
            self.env["pod.encounter"].create(
                {"patient_id": self.patient.id, "practice_id": False}
            )

    def test_res_partner(self):
        vals = {"name": "Prova"}
        exemple = self.env["res.partner"].create(vals)
        exemple.write(
            {"encounter_sequence_prefix": self.practice.encounter_sequence_prefix}
        )
        exemple.write({"encounter_sequence_prefix": "O", "encounter_sequence_id": 15})
