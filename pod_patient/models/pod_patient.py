from odoo import fields, models


class Patient(models.Model):
    _name = "pod.patient"
    _description = "Podiatry Patient"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # card_number = fields.Char()
    partner_id = fields.Many2one(
        "res.partner", delegate=True, ondelete="cascade", required=True
    )

    # patient_id = fields.Many2one('res.partner', domain=[(
    #     'is_patient', '=', True)], string="Patient", required=True)
