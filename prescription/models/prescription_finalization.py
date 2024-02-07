from odoo import fields, models


class PrescriptionFinalization(models.Model):
    _description = "Prescription Finalization Reason"
    _name = "prescription.finalization"
    _order = "name"

    active = fields.Boolean(default=True)
    name = fields.Char(
        string="Reason Name",
        required=True,
        translate=True,
        copy=False,
    )
    company_id = fields.Many2one(comodel_name="res.company")

    _sql_constraints = [
        (
            "name_company_uniq",
            "unique (name, company_id)",
            "Finalization name already exists !",
        ),
    ]
