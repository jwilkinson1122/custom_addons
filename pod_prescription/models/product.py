from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Product(models.Model):
    _inherit = "product.template"

    is_prescription = fields.Boolean(default=False)
    sct_code_id = fields.Many2one(
        string="SNOMED CT code",
        comodel_name="pod.sct.concept",
        domain=[("is_prescription_code", "=", True)],
        help="SNOMED CT Prescription Codes",
    )  
    
    atc_code_id = fields.Many2one(
        string="ATC code",
        comodel_name="pod.atc.concept",
        help="ATC prescription classification",
    )
    
    over_the_counter = fields.Boolean(
        default=False,
        help="True if prescription does not require a prescription",
    )  # FHIR Field: isOverTheCounter
    
    form_id = fields.Many2one(
        string="Form code",
        comodel_name="pod.sct.concept",
        domain=[("is_prescription_form", "=", True)],
        help="SNOMED CT Form Codes",
    )  # FHIR Field: form

    @api.constrains("type", "is_prescription")
    def _check_prescription(self):
        if self.is_prescription:
            if self.type not in ["product", "consu"]:
                raise ValidationError(
                    _("Prescription must be a stockable product")
                )
