 

from odoo import api, fields, models


class ProductConfiguratorSale(models.TransientModel):

    _name = "product.configurator.sale"
    _inherit = "product.configurator"
    _description = "Product Configurator Sale"

    # folio_id = fields.Many2one(comodel_name="sale.order", required=True, readonly=True)
    # order_line_id = fields.Many2one(comodel_name="hotel.folio.line", readonly=True)
    # folio_id = fields.Many2one(comodel_name="hotel.folio", required=True, readonly=True)
    folio_id = fields.Many2one(comodel_name="hotel.folio", readonly=True)
    order_line_id = fields.Many2one(comodel_name="hotel.folio.line", readonly=True)

    def _get_order_line_vals(self, product_id):
        """Hook to allow custom line values to be put on the newly
        created or edited lines."""
        product = self.env["product.product"].browse(product_id)
        line_vals = {"product_id": product_id, "folio_id": self.folio_id.id}
        # extra_vals = self.order_line_id._prepare_add_missing_fields(line_vals)
        # line_vals.update(extra_vals)
        line_vals.update(
            {
                "config_session_id": self.config_session_id.id,
                "name": product._get_mako_tmpl_name(),
                "customer_lead": product.sale_delay,
            }
        )
        return line_vals

    def action_config_done(self):
        """Parse values and execute final code before closing the wizard"""
        res = super(ProductConfiguratorSale, self).action_config_done()
        if res.get("res_model") == self._name:
            return res
        model_name = "hotel.folio.line"
        line_vals = self._get_order_line_vals(res["res_id"])

        # Call onchange explicite as write and create
        # will not trigger onchange automatically
        order_line_obj = self.env[model_name]
        cfg_session = self.config_session_id
        specs = cfg_session.get_onchange_specifications(model=model_name)
        updates = order_line_obj.onchange(line_vals, ["product_id"], specs)
        values = updates.get("value", {})
        values = cfg_session.get_vals_to_write(values=values, model=model_name)
        values.update(line_vals)

        if self.order_line_id:
            self.order_line_id.write(values)
        else:
            self.folio_id.write({"order_line": [(0, 0, values)]})
        return

    @api.model
    def create(self, vals):
        if self.env.context.get("default_order_line_id", False):
            sale_line = self.env["hotel.folio.line"].browse(
                self.env.context["default_order_line_id"]
            )
            if sale_line.custom_value_ids:
                vals["custom_value_ids"] = self._get_custom_values(
                    sale_line.config_session_id
                )
            if sale_line.config_session_id:
                vals["config_session_id"] = sale_line.config_session_id.id
            if sale_line.config_session_id.value_ids:
                vals["value_ids"] = [[6, False, sale_line.config_session_id.value_ids.ids]]
        res = super(ProductConfiguratorSale, self).create(vals)
        return res

    def _get_custom_values(self, session):
        custom_values = [(5,)] + [
            (
                0,
                0,
                {
                    "attribute_id": value_custom.attribute_id.id,
                    "value": value_custom.value,
                    "attachment_ids": [
                        (4, attach.id) for attach in value_custom.attachment_ids
                    ],
                },
            )
            for value_custom in session.custom_value_ids
        ]
        return custom_values
