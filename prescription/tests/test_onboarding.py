

from odoo.addons.onboarding.tests.case import TransactionCaseOnboarding


class TestOnboarding(TransactionCaseOnboarding):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_payment_provider_step = cls.env.ref(
            "account_payment.onboarding_onboarding_step_payment_provider"
        )
        cls.prescription_quotation_order_confirmation_step = cls.env.ref(
            "prescription.onboarding_onboarding_step_prescription_confirmation"
        )

    def test_payment_provider_account_doesnt_validate_prescription(self):
        self.assert_step_is_not_done(self.prescription_quotation_order_confirmation_step)
        self.env["onboarding.onboarding.step"].action_validate_step_payment_provider()
        self.assert_step_is_not_done(self.prescription_quotation_order_confirmation_step)

        # Set field as in payment_provider_onboarding_wizard's add_payment_method override
        self.env.company.prescription_onboarding_payment_method = "stripe"
        self.env["onboarding.onboarding.step"].action_validate_step_payment_provider()
        self.assert_step_is_done(self.prescription_quotation_order_confirmation_step)

    def test_payment_provider_prescription_validates_account(self):
        self.assert_step_is_not_done(self.account_payment_provider_step)
        self.env["onboarding.onboarding.step"].action_validate_step_payment_provider()
        self.assert_step_is_done(self.account_payment_provider_step)
