# -*- coding: utf-8 -*-


from odoo import api, fields, models


class PrescriptionOrderTemplateOption(models.Model):
    _name = "prescriptions.order.template.option"
    _description = "Device Template Option"
    _check_company_auto = True

    prescriptions_order_template_id = fields.Many2one(
        comodel_name='prescriptions.order.template',
        string="Device Template Reference",
        index=True, required=True,
        ondelete='cascade')

    company_id = fields.Many2one(
        related='prescriptions_order_template_id.company_id', store=True, index=True)

    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True, check_company=True,
        domain=lambda self: self._product_id_domain())

    name = fields.Text(
        string="Description",
        compute='_compute_name',
        store=True, readonly=False, precompute=True,
        required=True, translate=True)

    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_uom_id',
        store=True, readonly=False,
        required=True, precompute=True,
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    quantity = fields.Float(
        string="Quantity",
        required=True,
        digits='Product Unit of Measure',
        default=1)

    #=== COMPUTE METHODS ===#

    @api.depends('product_id')
    def _compute_name(self):
        for option in self:
            if not option.product_id:
                continue
            option.name = option.product_id.get_product_multiline_description_prescription()

    @api.depends('product_id')
    def _compute_uom_id(self):
        for option in self:
            option.uom_id = option.product_id.uom_id

    #=== BUSINESS METHODS ===#

    @api.model
    def _product_id_domain(self):
        """Returns the domain of the products that can be added as a template option."""
        return [('prescriptions_ok', '=', True)]

    def _prepare_option_line_values(self):
        """ Give the values to create the corresponding option line.

        :return: `prescriptions.order.option` create values
        :rtype: dict
        """
        self.ensure_one()
        return {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': self.quantity,
            'uom_id': self.uom_id.id,
        }
