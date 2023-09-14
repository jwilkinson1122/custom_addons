from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_pod = fields.Boolean(default=False, readonly=True)
    show_patient = fields.Boolean(default=False, readonly=True)
    show_subscriber = fields.Boolean(default=False, readonly=True)
    show_authorization = fields.Boolean(default=False, readonly=True)
    encounter_id = fields.Many2one("pod.encounter", readonly=True)
    coverage_template_id = fields.Many2one("pod.coverage.template")

    def _get_refund_common_fields(self):
        return super()._get_refund_common_fields() + [
            "is_pod",
            "show_patient",
            "show_subscriber",
            "show_authorization",
            "encounter_id",
        ]


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    patient_id = fields.Many2one("pod.patient", readonly=True)
    encounter_id = fields.Many2one("pod.encounter", readonly=True)
    is_pod = fields.Boolean(related="move_id.is_pod", readonly=True)
    patient_name = fields.Char()
    subscriber_id = fields.Char()
    authorization_number = fields.Char()
