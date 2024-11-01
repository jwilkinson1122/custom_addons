from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_config_start(self):
        """Return action to start configuration wizard"""
        configurator_obj = self.env["product.configurator.sale"]
        ctx = dict(
            self.env.context,
            default_order_id=self.id,
            wizard_model="product.configurator.sale",
            allow_preset_selection=True,
        )
        return configurator_obj.with_context(**ctx).get_wizard_action()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    custom_value_ids = fields.One2many(
        comodel_name="product.config.session.custom.value",
        inverse_name="cfg_session_id",
        related="config_session_id.custom_value_ids",
        string="Configurator Custom Values",
    )
    config_ok = fields.Boolean(
        related="product_id.config_ok", string="Configurable", readonly=True
    )
    config_session_id = fields.Many2one(
        comodel_name="product.config.session", string="Config Session"
    )

    def reconfigure_product(self):
        """Creates and launches a product configurator wizard with a linked
        template and variant in order to re-configure a existing product. It is
        esetially a shortcut to pre-fill configuration data of a variant"""
        wizard_model = "product.configurator.sale"

        extra_vals = {
            "order_id": self.order_id.id,
            "order_line_id": self.id,
            "product_id": self.product_id.id,
        }
        self = self.with_context(
            default_order_id=self.order_id.id,
            default_order_line_id=self.id,
        )
        return self.product_id.product_tmpl_id.create_config_wizard(
            model_name=wizard_model, extra_vals=extra_vals
        )

    @api.depends()
    def _compute_price_unit(self):
        result = None
        for line in self:
            if line.config_session_id:
                account_tax_obj = self.env["account.tax"]
                line.price_unit = account_tax_obj._fix_tax_included_price_company(
                    line.config_session_id.price,
                    line.product_id.taxes_id,
                    line.tax_id,
                    line.company_id,
                )
            else:
                result = super(SaleOrderLine, line)._compute_price_unit()
        return result

    def _get_sale_order_line_multiline_description_variants(self):
        name = ""
        for line in self:
            custom_values = line.custom_value_ids
            if custom_values:
                name += "\n" + "\n".join(
                    [f"{cv.display_name}: {cv.value}" for cv in custom_values]
                )
            else:
                name += super(
                    SaleOrderLine,
                    line,
                )._get_sale_order_line_multiline_description_variants()
        return name

    def write(self, vals):
        res = super().write(vals)
        if "product_no_variant_attribute_value_ids" in vals:
            for sol in self:
                sol_pav = sol.product_no_variant_attribute_value_ids
                sol_pav_to_store = sol_pav.filtered("attribute_id.store_in_field")
                sol_pav_custom = sol.product_custom_attribute_value_ids
                pav_vals = {}
                for pav in sol_pav_to_store:
                    field_name = pav.attribute_id.store_in_field.name
                    value = (
                        sol_pav_custom.filtered(
                            lambda x: x.custom_product_template_attribute_value_id
                            == pav
                        ).custom_value
                        or pav.name
                    )
                    pav_vals[field_name] = value
                if pav_vals:
                    super().write(pav_vals)
        return res
