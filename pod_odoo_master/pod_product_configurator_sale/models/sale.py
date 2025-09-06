import json
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # order_line = fields.One2many(
    #     comodel_name='sale.order.line',
    #     inverse_name='order_id',
    #     string="Order Lines",
    #     copy=True, auto_join=True)

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

    template_id = fields.Many2one(
        "product.configurator.template",
        string="Configuration Template",
        help="Select a previously saved configuration template."
    )

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

    laterality = fields.Selection(
        selection=[("left", "Left Only"), ("right", "Right Only"), ("bilateral", "Bilateral")],
        string="Laterality",
        required=True,
        default="bilateral",
        help="Specifies whether this order line is for the left foot, right foot, or both.",
    )

    price_left = fields.Float("Left Foot Price", compute="_compute_price_breakdown", store=True)
    price_right = fields.Float("Right Foot Price", compute="_compute_price_breakdown", store=True)
    price_per_foot = fields.Float("Price Per Foot", compute="_compute_price_per_foot", store=True)
    previous_price_left = fields.Float("Previous Left Foot Price", store=True)
    previous_price_right = fields.Float("Previous Right Foot Price", store=True)

    def _default_laterality_config(self):
        # Get the last confirmed sale order (or whatever logic you need)
        last_order = self.env["sale.order"].search([], order="date_order desc", limit=1)
        if last_order:
            last_line = self.env["sale.order.line"].search([
                ("order_id", "=", last_order.id),
                ("product_template_id", "!=", False)
            ], order="id desc", limit=1)
            return last_line.laterality_config_ids if last_line else False
        return False

    laterality_config_ids = fields.One2many(
        "product.configurator.laterality.line",
        "sale_order_line_id",
        string="Laterality Configurations",
        default=_default_laterality_config
    )

    previous_config_comparison = fields.Text(
        compute="_compute_previous_config_comparison",
        store=False,
        string="Previous Configuration Comparison"
    )

    exclude_from_bulk_copy = fields.Boolean(
        string="Exclude from Bulk Copy",
        help="Check this box if you do not want this product to be included in bulk copying of configurations."
    )


    @api.depends("product_id", "laterality_config_ids")
    def _compute_custom_name(self):
        """Append laterality and custom configurations to product name dynamically."""
        for line in self:
            custom_details = [
                f"{config.attribute_id.name}: {config.value_id.name}"
                for config in line.laterality_config_ids
            ]
            details_text = ", ".join(custom_details) if custom_details else "No Customization"

            line.name = f"{line.product_id.name} ({line.laterality}) - {details_text}"

    @api.depends("laterality", "order_line")
    def _compute_auto_copy_laterality(self):
        """Automatically copy laterality configurations in sale order if needed."""
        for order in self:
            if order.laterality == "bilateral":
                left_lines = order.order_line.filtered(lambda l: l.laterality == "left")
                right_lines = order.order_line.filtered(lambda l: l.laterality == "right")

                if not right_lines:
                    # Auto-copy left to right
                    for line in left_lines:
                        order.order_line += line.copy(default={"laterality": "right"})

    def reconfigure_product(self):
        """Launches the configurator wizard to reconfigure an existing product."""
        wizard_model = "product.configurator.sale"

        extra_vals = {
            "order_id": self.order_id.id,
            "order_line_id": self.id,
            "product_id": self.product_id.id,
        }
        self = self.with_context(
            default_order_id=self.order_id.id,
            default_order_line_id=self.id,
            default_config_session_id=self.config_session_id.id,  # Ensure configurator session persists
        )
        return self.product_id.product_tmpl_id.create_config_wizard(
            model_name=wizard_model, extra_vals=extra_vals
        )

    @api.depends("product_id", "laterality", "laterality_config_ids", "order_id.partner_id")
    def _compute_previous_config_comparison(self):
        for line in self:
            # skip during unlink/recycle-bin reads
            if self.env.context.get('no_prev_config_cmp'):
                line.previous_config_comparison = False
                continue

            partner = line.order_id.partner_id
            prev = self._find_previous_line(
                partner_id=partner.id if partner else False,
                product_id=line.product_id.id,
                laterality=line.laterality,
                exclude_order_id=line.order_id.id if line.order_id else None,
            )

            comparison = []
            if prev:
                current_config = {c.attribute_id.id: c.value_id.name for c in line.laterality_config_ids}
                past_config    = {c.attribute_id.id: c.value_id.name for c in prev.laterality_config_ids}
                all_attr_ids = set(current_config) | set(past_config)
                for attr_id in all_attr_ids:
                    comparison.append({
                        "attribute": self.env["product.attribute"].browse(attr_id).name,
                        "current_value": current_config.get(attr_id, "Not Set"),
                        "past_value": past_config.get(attr_id, "Not Set"),
                        "difference": current_config.get(attr_id) != past_config.get(attr_id),
                    })
            line.previous_config_comparison = json.dumps(comparison)
    
    def action_compare_to_previous(self):
        """Show a popup with differences between current and past configurations."""
        self.ensure_one()
        comparison_data = json.loads(self.previous_config_comparison or "[]")
        differences = [row for row in comparison_data if row["difference"]]

        if not differences:
            return {"warning": {"title": "No Differences", "message": "This configuration matches the last order."}}

        message = "<b>Differences detected:</b><br/><ul>"
        for diff in differences:
            message += f"<li><b>{diff['attribute']}:</b> Previous: {diff['past_value']} | Current: {diff['current_value']}</li>"
        message += "</ul>"

        return {
            "type": "ir.actions.act_window",
            "name": "Review Configuration Differences",
            "res_model": "ir.actions.server",
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
            "context": {"default_message": message},
        }

    def action_copy_previous_configuration(self):
            self.ensure_one()
            prev = self._find_previous_line(
                partner_id=self.order_id.partner_id.id if self.order_id.partner_id else False,
                product_id=self.product_id.id,
                laterality=self.laterality,
                exclude_order_id=self.order_id.id if self.order_id else None,
            )
            if not prev:
                return {"warning": {"title": "No Previous Configuration Found", "message": "There is no previous configuration available for this product."}}

            self.laterality_config_ids = [(0, 0, {
                "side": c.side,
                "attribute_id": c.attribute_id.id,
                "value_id": c.value_id.id,
            }) for c in prev.laterality_config_ids]
            return {"info": {"title": "Configuration Copied", "message": "Previous configuration has been applied successfully."}}

    def action_bulk_copy_previous_configurations(self):
        for order in self:
            for line in order.order_line.filtered(lambda l: not l.exclude_from_bulk_copy):
                prev = self._find_previous_line(
                    partner_id=order.partner_id.id if order.partner_id else False,
                    product_id=line.product_id.id,
                    laterality=line.laterality,
                    exclude_order_id=order.id,
                )
                if prev:
                    line.laterality_config_ids = [(0, 0, {
                        "side": c.side,
                        "attribute_id": c.attribute_id.id,
                        "value_id": c.value_id.id,
                    }) for c in prev.laterality_config_ids]
        return {"info": {"title": "Bulk Copy Successful", "message": "Previous configurations have been applied to all selected products."}}

    
    def action_confirm_bulk_copy(self):
        """Display a confirmation dialog before applying bulk copy."""
        return {
            "type": "ir.actions.act_window",
            "name": "Confirm Bulk Copy",
            "res_model": "ir.actions.server",
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
            "context": {"default_message": "Are you sure you want to apply bulk copying? This will overwrite configurations for all selected products."},
        }

    def action_reset_excluded_products(self):
        """Resets the configurations of only the excluded products in the order."""
        for order in self:
            for line in order.order_line.filtered(lambda l: l.exclude_from_bulk_copy):
                line.laterality_config_ids = [(5, 0, 0)]  # Clear configurations

        return {"info": {"title": "Excluded Products Reset", "message": "Configurations for excluded products have been reset."}}

    def action_save_configuration_template(self):
        """Save the current product configuration as a reusable template."""
        for order in self:
            for line in order.order_line:
                template_vals = {
                    "name": f"{line.product_id.name} - {line.laterality} Template",
                    "product_id": line.product_id.id,
                    "laterality": line.laterality,
                    "laterality_config_ids": [(0, 0, {
                        "side": config.side,
                        "attribute_id": config.attribute_id.id,
                        "value_id": config.value_id.id,
                    }) for config in line.laterality_config_ids]
                }
                self.env["product.configurator.template"].create(template_vals)

        return {"info": {"title": "Template Saved", "message": "Configuration has been saved as a template."}}

    def action_apply_configuration_template(self, template_id):
        """Apply a saved configuration template to the current order."""
        template = self.env["product.configurator.template"].browse(template_id)

        for order in self:
            for line in order.order_line.filtered(lambda l: l.product_id == template.product_id):
                copied_values = [(0, 0, {
                    "side": config.side,
                    "attribute_id": config.attribute_id.id,
                    "value_id": config.value_id.id,
                }) for config in template.laterality_config_ids]

                line.update({
                    "laterality": template.laterality,
                    "laterality_config_ids": copied_values,
                })

        return {"info": {"title": "Template Applied", "message": "The configuration has been applied to your order."}}

    # @api.depends("product_id", "laterality", "product_uom_qty", "laterality_config_ids")
    # def _compute_price_per_foot(self):
    #     """Dynamically adjust pricing based on laterality selection and custom configurations."""
    #     for line in self:
    #         base_price = line.product_id.lst_price
    #         price_adjustment = sum(config.value_id.price_extra for config in line.laterality_config_ids)
    #         if not line.price_unit or line.price_unit == line.product_id.lst_price:
    #             if line.laterality == "left":
    #                 line.price_unit = base_price + price_adjustment
    #             elif line.laterality == "right":
    #                 line.price_unit = base_price + price_adjustment
    #             elif line.laterality == "bilateral":
    #                 line.price_unit = (base_price + price_adjustment) * 2   


    # product_uom_qty = fields.Float(
    #     string="Quantity",
    #     compute='_compute_product_uom_qty',
    #     digits='Product Unit of Measure', default=1.0,
    #     store=True, readonly=False, required=True, precompute=True)


    @api.depends("product_id", "laterality", "product_uom_qty")
    def _compute_price_per_foot(self):
        """Dynamically adjust pricing based on laterality selection and quantity."""
        for line in self:
            base_price = line.product_id.lst_price
            quantity = line.product_uom_qty or 1  # Ensure there's a default quantity

            if line.laterality in ["left", "right"]:
                line.price_unit = base_price * quantity
            elif line.laterality == "bilateral":
                line.price_unit = base_price * (2 * quantity)  # Two feet



    @api.depends("product_id", "laterality", "price_unit")
    def _compute_price_breakdown(self):
        """Ensure the price is split correctly between left and right feet without modifying price_unit."""
        for line in self:
            if line.laterality == "bilateral":
                left_price = line.price_unit / 2
                right_price = line.price_unit / 2
            else:
                left_price = line.price_unit if line.laterality == "left" else 0.0
                right_price = line.price_unit if line.laterality == "right" else 0.0

            line.update({
                "price_left": left_price,
                "price_right": right_price,
            })

    def action_review_pricing_changes(self):
        """Show a popup with pricing differences before finalizing."""
        self.ensure_one()
        message = "<b>Pricing Changes Detected:</b><br/><ul>"

        if self.price_left != self.previous_price_left:
            message += f"<li><b>Left Foot Price:</b> Previous: {self.previous_price_left}, New: {self.price_left}</li>"
        
        if self.price_right != self.previous_price_right:
            message += f"<li><b>Right Foot Price:</b> Previous: {self.previous_price_right}, New: {self.price_right}</li>"

        message += "</ul>"

        return {
            "type": "ir.actions.act_window",
            "name": "Review Pricing Changes",
            "res_model": "ir.actions.server",
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
            "context": {"default_message": message},
        }

    def _prepare_invoice_line(self, **optional_values):
        """Ensure laterality is included in invoices"""
        invoice_vals = super()._prepare_invoice_line(**optional_values)
        invoice_vals.update({"laterality": self.laterality})
        return invoice_vals

    def _get_sale_order_line_multiline_description_variants(self):
        name = super(SaleOrderLine, self)._get_sale_order_line_multiline_description_variants()
        
        for line in self:
            custom_values = line.custom_value_ids
            if custom_values:
                name += "\n" + "\n".join(
                    f"{cv.display_name}: {cv.value}" for cv in custom_values
                )
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
