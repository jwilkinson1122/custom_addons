
from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Groups
    # group_product_variant = fields.Boolean("Variants", implied_group='product.group_product_variant')

    module_prescription_product_matrix = fields.Boolean("Prescription Grid Entry")

    group_prescription_manual_finalization = fields.Boolean(
        string="Finish Prescription manually choosing a reason",
        help="Allow to finish an Prescription without returning back a product or refunding",
        implied_group="prescription.group_prescription_manual_finalization",
    )
    prescription_return_grouping = fields.Boolean(
        related="company_id.prescription_return_grouping",
        readonly=False,
    )
    send_prescription_confirmation = fields.Boolean(
        related="company_id.send_prescription_confirmation",
        readonly=False,
    )
    prescription_mail_confirmation_template_id = fields.Many2one(
        related="company_id.prescription_mail_confirmation_template_id",
        readonly=False,
    )
    send_prescription_receipt_confirmation = fields.Boolean(
        related="company_id.send_prescription_receipt_confirmation",
        readonly=False,
    )
    prescription_mail_receipt_confirmation_template_id = fields.Many2one(
        related="company_id.prescription_mail_receipt_confirmation_template_id",
        readonly=False,
    )
    send_prescription_draft_confirmation = fields.Boolean(
        related="company_id.send_prescription_draft_confirmation",
        readonly=False,
    )
    prescription_mail_draft_confirmation_template_id = fields.Many2one(
        related="company_id.prescription_mail_draft_confirmation_template_id",
        readonly=False,
    )

    # @api.onchange('group_product_variant')
    # def _onchange_group_product_variant(self):
    #     """The product Configurator requires the product variants activated.
    #     If the user disables the product variants -> disable the product configurator as well"""
    #     if self.module_prescription_product_matrix and not self.group_product_variant:
    #         self.module_prescription_product_matrix = False
