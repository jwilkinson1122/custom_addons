from odoo import api, exceptions, fields, models


class PrescriptionLine(models.Model):
    _name = "pod.prescription.line"
    _description = "Prescription Request Line"

    prescription_id = fields.Many2one("pod.prescription", required=True)
    patient_id = fields.Many2one("pod.patient", required=True)
    note = fields.Char("Notes")
    foot_image = fields.Binary(related="patient_id.image")
    foot_image2 = fields.Binary(related="patient_id.image2")
