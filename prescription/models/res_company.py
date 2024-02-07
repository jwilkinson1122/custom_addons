
from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    additional_hours = fields.Integer(
        help="Provide the min hours value for \
                                      bookin, bookout days, whatever the \
                                      hours will be provided here based on \
                                      that extra days will be calculated.",
    )


    def _default_prescription_mail_confirmation_template(self):
        try:
            return self.env.ref("prescription.mail_template_prescription_notification").id
        except ValueError:
            return False

    def _default_prescription_mail_receipt_template(self):
        try:
            return self.env.ref("prescription.mail_template_prescription_receipt_notification").id
        except ValueError:
            return False

    def _default_prescription_mail_draft_template(self):
        try:
            return self.env.ref("prescription.mail_template_prescription_draft_notification").id
        except ValueError:
            return False

    prescription_return_grouping = fields.Boolean(
        string="Group Prescription returns by customer address and warehouse",
        default=True,
    )
    send_prescription_confirmation = fields.Boolean(
        string="Send Prescription Confirmation",
        help="When the delivery is confirmed, send a confirmation email "
        "to the customer.",
    )
    send_prescription_receipt_confirmation = fields.Boolean(
        string="Send Prescription Receipt Confirmation",
        help="When the Prescription receipt is confirmed, send a confirmation email "
        "to the customer.",
    )
    send_prescription_draft_confirmation = fields.Boolean(
        string="Send Prescription draft Confirmation",
        help="When a customer places an Prescription, send a notification with it",
    )
    prescription_mail_confirmation_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template confirmation for Prescription",
        domain="[('model', '=', 'prescription')]",
        default=_default_prescription_mail_confirmation_template,
        help="Email sent to the customer once the Prescription is confirmed.",
    )
    prescription_mail_receipt_confirmation_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template receipt confirmation for Prescription",
        domain="[('model', '=', 'prescription')]",
        default=_default_prescription_mail_receipt_template,
        help="Email sent to the customer once the Prescription products are received.",
    )
    prescription_mail_draft_confirmation_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template draft notification for Prescription",
        domain="[('model', '=', 'prescription')]",
        default=_default_prescription_mail_draft_template,
        help="Email sent to the customer when they place " "an Prescription from the portal",
    )

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        for company in companies:
            company.create_prescription_index()
        return companies

    def create_prescription_index(self):
        return (
            self.env["ir.sequence"]
            .sudo()
            .create(
                {
                    "name": _("Prescription Code"),
                    "prefix": "Prescription",
                    "code": "prescription",
                    "padding": 4,
                    "company_id": self.id,
                }
            )
        )
