

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Groups
    group_product_variant = fields.Boolean("Variants", implied_group='product.group_product_variant')

    module_prescription_product_matrix = fields.Boolean("Prescriptions Grid Entry")
    
    #=== ONCHANGE METHODS ===#
    
    @api.onchange('group_product_variant')
    def _onchange_group_product_variant(self):
        """The product Configurator requires the product variants activated.
        If the user disables the product variants -> disable the product configurator as well"""
        if self.module_prescription_product_matrix and not self.group_product_variant:
            self.module_prescription_product_matrix = False

