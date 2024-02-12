# -*- coding: utf-8 -*-


from odoo import api, fields, models


class PrescriptionLine(models.Model):
    _inherit = "prescription.line"
    _description = "Prescription Order Line"

    prescription_option_ids = fields.One2many('prescription.option', 'line_id', 'Optional Products Lines')

    @api.depends('product_id')
    def _compute_name(self):
        # Take the description on the order template if the product is present in it
        super()._compute_name()
        for line in self:
            if line.product_id and line.order_id.prescription_template_id and line._use_template_name():
                for template_line in line.order_id.prescription_template_id.prescription_template_line_ids:
                    if line.product_id == template_line.product_id:
                        lang = line.order_id.partner_id.lang
                        line.name = template_line.with_context(lang=lang).name + line.with_context(lang=lang)._get_prescription_line_multiline_description_variants()
                        break

    def _use_template_name(self):
        """ Allows overriding to avoid using the template lines descriptions for the prescription order lines descriptions.
    This is typically useful for 'configured' products, such as event_ticket or event_booth, where we need to have
    specific configuration information inside description instead of the default values.
    """
        self.ensure_one()
        return True

    def _compute_price_unit(self):
        # Avoid recomputing the price with pricelist rules, use the initial price
        # used in the optional product line.
        lines_without_price_recomputation = self._lines_without_price_recomputation()
        super(PrescriptionLine, self - lines_without_price_recomputation)._compute_price_unit()

    def _lines_without_price_recomputation(self):
        """ Hook to allow filtering the lines to avoid the recomputation of the price. """
        return self.filtered('prescription_option_ids')

    #=== TOOLING ===#

    def _can_be_edited_on_portal(self):
        return self.order_id._can_be_edited_on_portal() and (
            self.prescription_option_ids
            or self.product_id in self.order_id.prescription_option_ids.product_id
        )
