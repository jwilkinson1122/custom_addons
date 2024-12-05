from odoo import http
from odoo.http import request
import json
import logging
from datetime import datetime

log = logging.getLogger(__name__)


class PartnerController(http.Controller):

    @http.route("/get/saleOrders", type="http", auth="public", methods=["GET"])
    def get_sales_order(self, **kw):
        """
        HTTP GET endpoint to retrieve sale order information based on order reference.

        :param kw: contains the order reference value for querying the sales order
        :return: JSON response with sale order details or error message.
        """
        reference = kw.get("order_reference")
        if not reference:
            return f"No order reference was given"

        order = (
            request.env["sale.order"].sudo().search([("name", "=", reference)], limit=1)
        )
        if not order:
            return f"No order could be found with the following reference: {reference}"

        order_info = [
            {
                "order_id": order.id,
                "reference": order.name,
                "order_date": order.date_order.strftime("%Y-%m-%d %H:%M:%S"),
                "partner_id": order.partner_id.id,
                "partner_name": order.partner_id.name,
                "line_details": [
                    {
                        "line_id": line.id,
                        "product_id": line.product_id.id,
                        "product_sku": line.product_id.default_code,
                        "product_name": line.product_id.name,
                        "quantity": line.product_uom_qty,
                        "uom": "EA",
                        "unit_price": line.price_unit,
                        "price_total": line.price_subtotal,
                    }
                    for line in order.order_line
                ],
            }
        ]

        return request.make_response(
            json.dumps(order_info), headers=[("Content-Type", "application/json")]
        )

    @http.route(
        "/createCustomer", type="http", auth="public", methods=["POST"], csrf=False
    )
    def create_customer(self, **kw):
        """
        HTTP POST endpoint to create a new customer

        :param kw: contains the customer name used to create the new customer record.
        :return: Success or error message.
        """
        customer_name = kw.get("customer_name")
        if customer_name:
            try:
                # Prevents duplicate customer records
                existing_customer = (
                    request.env["res.partner"]
                    .sudo()
                    .search([("name", "=", customer_name)], limit=1)
                )
                if existing_customer:
                    return f"Error: Customer alredy exists for {customer_name}!"

                request.env["res.partner"].sudo().create({"name": customer_name})
                return f"Success: Customer record created for {customer_name}!"

            except Exception as e:
                log.error(f"Error creating customer:{e}")
                return (
                    f"Error: Customer record could not be created for {customer_name}!"
                )

        return "Error: No customer name was given, customer could not be created!"
