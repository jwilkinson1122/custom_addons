import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class MultiStepWizard(models.AbstractModel):
    _name = "multi.step.wizard.mixin"
    _description = "Multi Steps Wizard Mixin"

    state = fields.Selection(
        selection="_selection_state", default="start", required=True
    )
    allow_back = fields.Boolean(compute="_compute_allow_back")

    @api.depends("state")
    def _compute_allow_back(self):
        for record in self:
            # Allow back if a state_previous method exists for the current state
            record.allow_back = hasattr(record, f"state_previous_{record.state}")

    def state_previous_configure(self):
        self.state = "start"

    def state_previous_custom(self):
        self.state = "configure"

    def state_previous_summary(self):
        self.state = "custom"

    @api.model
    def _selection_state(self):
        return [
            ("start", "Start"),
            ("configure", "Configure"),
            ("custom", "Customize"),
            ("summary", "Summary"),
            ("final", "Final"),
        ]

    def open_next(self):
        state_method = getattr(self, f"state_exit_{self.state}", None)
        if not state_method:
            raise NotImplementedError(f"No method defined for state {self.state}")
        state_method()
        return self._reopen_self()

    def open_previous(self):
        state_method = getattr(self, f"state_previous_{self.state}", None)
        if not state_method:
            raise NotImplementedError(f"No method defined for state {self.state}")
        state_method()
        return self._reopen_self()

    def _reopen_self(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def state_exit_start(self):
        raise NotImplementedError("Define the next state in the inheriting wizard.")

    def state_exit_configure(self):
        raise NotImplementedError("Define the next state in the inheriting wizard.")

    def submit_wizard(self):
        """Submit the wizard and redirect back to the sales order form view."""
        if self.sale_order_id:
            product_id = (
                self.product_variant_id.id
                if self.product_variant_id
                else self.product_id.id
            )
            
            # Build the sale order line description with each selection on a new line
            description = (
                f"{self.product_id.display_name}\n"
                f"Configuration 1: {self.field1 or 'N/A'}\n"
                f"Configuration 2: {self.field2 or 'N/A'}\n"
                f"Customization: {self.field3 or 'N/A'}"
            )
            
            # Create the sale order line
            order_line_values = {
                "order_id": self.sale_order_id.id,
                "product_id": product_id,
                "product_uom_qty": 1,
                "price_unit": self.computed_price,
                "name": description,
            }
            self.env["sale.order.line"].create(order_line_values)
        
        # Redirect back to the sale order
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": self.sale_order_id.id,
            "view_mode": "form",
            "target": "current",
        }


    # def submit_wizard(self):
    #     """Submit the wizard and redirect back to the sales order form view."""
    #     if self.sale_order_id:
    #         product_id = (
    #             self.product_variant_id.id
    #             if self.product_variant_id
    #             else self.product_id.id
    #         )
    #         order_line_values = {
    #             "order_id": self.sale_order_id.id,
    #             "product_id": product_id,
    #             "product_uom_qty": 1,
    #             "price_unit": self.computed_price,
    #             "name": f"{self.product_id.display_name}: {self.field1}, {self.field2}, {self.field3}",
    #         }
    #         self.env["sale.order.line"].create(order_line_values)

    #     return {
    #         "type": "ir.actions.act_window",
    #         "res_model": "sale.order",
    #         "res_id": self.sale_order_id.id,
    #         "view_mode": "form",
    #         "target": "current",
    #     }
