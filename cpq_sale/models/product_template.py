
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cpq_description_sale_tmpl = fields.Text(
        string="Configurable Sale Description Template"
    )

    # def action_configure_cpq(self):
    #     self.ensure_one()

    #     if not self.id:
    #         self.order_id._compute_amount_all()
    #         self.order_id.write({'order_line': [(1, self._origin.id, {})]})
    #         self._cr.commit()

    #     return {
    #     "type": "ir.actions.client",
    #     "tag": "cpq.ConfigureDialogAction",
    #     "context": {
    #         "active_model": "sale.order.line",
    #         "active_id": self.id,
    #         "cpq_product_template_id": self.product_template_id.id,
    #         "cpq_initial_config": self.cpq_configuration_json or False,
    #         "orderId": self.order_id.id,
    #         "currencyId": self.order_id.currency_id.id,
    #         "soDate": str(self.order_id.date_order),
    #         "companyId": self.order_id.company_id.id,
    #     },
    # }

    def action_configure_cpq(self):
        self.ensure_one()

        # ✅ Step 1: Ensure sale.order exists
        order = self.env["sale.order"].search([("state", "=", "draft")], limit=1)
        if not order:
            order = self.env["sale.order"].create({
                "partner_id": self.env.user.partner_id.id,
            })

        # ✅ Step 2: Create draft order line for this template
        order_line = self.env["sale.order.line"].create({
            "order_id": order.id,
            "product_template_id": self.id,
            "product_id": self._ensure_configurator_product().id,
            "product_uom_qty": 1,
            "price_unit": self.list_price,
        })

        _logger.info(f"🧩 Created order line {order_line.id} for CPQ configuration.")

        return {
            "type": "ir.actions.client",
            "tag": "cpq.ConfigureDialogAction",
            "context": {
                "active_model": "sale.order.line",
                "active_id": order_line.id,  # ✅ CORRECT order line ID
                "cpq_product_template_id": self.id,
                "cpq_initial_config": order_line.cpq_configuration_json or False,
                "orderId": order.id,
                "currencyId": order.currency_id.id,
                "soDate": str(order.date_order),
                "companyId": order.company_id.id,
            },
        }

    def action_config_start_global(self):
        # Use existing draft or create new
        order = self.env["sale.order"].search([("state", "=", "draft")], limit=1)
        if not order:
            order = self.env["sale.order"].create({
                "partner_id": self.env.user.partner_id.id,
            })

        cpq_products = self.env["product.template"].search([("cpq_ok", "=", True)])
        if not cpq_products:
            raise UserError("No CPQ-enabled products found.")

        if len(cpq_products) == 1:
            return cpq_products[0].action_configure_cpq()

        # Otherwise, open product selection tree view
        return {
            "type": "ir.actions.act_window",
            "name": "Select CPQ Product",
            "res_model": "product.template",
            "view_mode": "tree",
            "domain": [("cpq_ok", "=", True)],
            "target": "current",
            "context": {
                "active_model": "sale.order",
                "active_id": order.id,
            },
        }