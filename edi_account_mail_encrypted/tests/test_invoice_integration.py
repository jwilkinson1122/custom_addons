import base64
import logging
from io import BytesIO

import mock

from odoo.tests import common
from odoo.tools.config import config

from odoo.addons.base.models.ir_actions_report import IrActionsReport
from odoo.addons.component.tests.common import SavepointComponentRegistryCase

_logger = logging.getLogger(__name__)
try:
    from cryptography.fernet import Fernet
    from PyPDF2 import PdfFileReader, PdfFileWriter
except ImportError as err:
    _logger.debug(err)


class EDIBackendTestCase(SavepointComponentRegistryCase, common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        self = cls
        config["email_integration_key"] = Fernet.generate_key()
        self._load_module_components(self, "component_event")
        self._load_module_components(self, "edi_oca")
        self._load_module_components(self, "edi_account_oca")
        self._load_module_components(self, "edi_account_mail")
        self._load_module_components(self, "edi_account_mail_encrypted")
        self.tax = self.env["account.tax"].create(
            {
                "name": "Test tax",
                "amount_type": "percent",
                "amount": 21,
                "type_tax_use": "sale",
            }
        )

        self.partner = self.env["res.partner"].create(
            {
                "name": "Cliente de prueba",
                "street": "C/ Ejemplo, 13",
                "zip": "13700",
                "city": "Tomelloso",
                "country_id": self.env.ref("base.es").id,
                "vat": "ES05680675C",
                "send_invoice_by_mail": True,
                "email_integration": "demo@demo.es",
                "invoice_report_email_id": self.env.ref("account.account_invoices").id,
            }
        )
        self.password = "1234"
        self.env["res.encrypt.value"].with_context(
            default_res_id=self.partner.id,
            default_model=self.partner._name,
            default_field="email_integration_password",
        ).create({"value": self.password}).encrypt_store()
        main_company = self.env.ref("base.main_company")
        main_company.vat = "ESA12345674"
        main_company.partner_id.country_id = self.env.ref("base.uk")
        self.sale_journal = self.env["account.journal"].create(
            {
                "name": "Sale journal",
                "code": "SALE_TEST",
                "type": "sale",
                "company_id": main_company.id,
            }
        )
        self.account = self.env["account.account"].create(
            {
                "company_id": main_company.id,
                "name": "Facturae Product account",
                "code": "facturae_product",
                "user_type_id": self.env.ref("account.data_account_type_revenue").id,
            }
        )
        self.move = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "journal_id": self.sale_journal.id,
                "invoice_date": "2016-03-12",
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref(
                                "product.product_delivery_02"
                            ).id,
                            "account_id": self.account.id,
                            "name": "Producto de prueba",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "tax_ids": [(6, 0, self.tax.ids)],
                        },
                    )
                ],
            }
        )
        self.move.refresh()

    def test_check_password(self):
        view_value = (
            self.env["res.view.value"]
            .with_context(
                default_res_id=self.partner.id,
                default_model=self.partner._name,
                default_field="email_integration_password",
            )
            .create({})
        )
        self.assertEqual(view_value.value, self.password)

    def test_send(self):
        self.assertTrue(self.partner.email_integration_password)
        with mock.patch.object(IrActionsReport, "_run_wkhtmltopdf") as patch:
            writer = PdfFileWriter()
            writer.addBlankPage(219, 297)
            buff = BytesIO()
            writer.write(buff)
            patch.return_value = buff.getvalue()
            self.move.with_context(
                force_edi_send=True,
                _edi_send_break_on_error=True,
                force_report_rendering=True,
            ).action_post()
            patch.assert_called()
        self.assertTrue(self.move.exchange_record_ids)
        self.assertRegex(self.move.exchange_record_ids.exchange_filename, r"^.*\.pdf")
        data = base64.b64decode(self.move.exchange_record_ids.exchange_file)
        in_buff = BytesIO(data)
        pdf = PdfFileReader(in_buff)
        self.assertTrue(pdf.decrypt(self.password))

    def test_send_zip(self):
        self.assertTrue(self.partner.email_integration_password)
        self.move.with_context(
            force_edi_send=True,
            _edi_send_break_on_error=True,
        ).action_post()
        self.assertTrue(self.move.exchange_record_ids)
        self.assertRegex(self.move.exchange_record_ids.exchange_filename, r"^.*\.zip$")
