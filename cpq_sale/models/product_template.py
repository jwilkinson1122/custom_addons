
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cpq_description_sale_tmpl = fields.Text(
        string="Configurable Sale Description Template"
    )

    def action_configure_cpq(self):
        self.ensure_one()

        ctx = self.env.context
        active_order_id = ctx.get("active_id")
        active_model = ctx.get("active_model")

        _logger.info(f"🧩 Configurator called for product {self.display_name} with context: {ctx}")

        sale_order = None

        if active_model == "sale.order" and active_order_id:
            sale_order = self.env["sale.order"].browse(active_order_id)
            _logger.info(f"🧾 Using active Sale Order {sale_order.name} ({sale_order.id}) from context.")
        elif active_model == "sale.order.line" and active_order_id:
            sale_order_line = self.env["sale.order.line"].browse(active_order_id)
            sale_order = sale_order_line.order_id
            _logger.info(f"🧾 Using Sale Order {sale_order.name} ({sale_order.id}) from sale order line context.")
        else:
            # Smart fallback: try to use existing draft order
            sale_order = self.env["sale.order"].search([("state", "=", "draft")], limit=1)
            if sale_order:
                _logger.info(f"🧾 Fallback to first draft Sale Order {sale_order.name} ({sale_order.id})")
            else:
                sale_order = self.env["sale.order"].create({
                    "partner_id": self.env.user.partner_id.id,
                })
                _logger.info(f"🆕 Created new draft Sale Order {sale_order.name} ({sale_order.id})")

        return {
            "type": "ir.actions.client",
            "tag": "cpq.ConfigureDialogAction",
            "context": {
                "active_model": "sale.order",
                "active_id": sale_order.id,
                "cpq_product_template_id": self.id,
                "cpq_initial_config": False,
                "redirect_to_line": True,
                "orderId": sale_order.id,
                "currencyId": sale_order.currency_id.id,
                "soDate": str(sale_order.date_order),
                "companyId": sale_order.company_id.id,
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