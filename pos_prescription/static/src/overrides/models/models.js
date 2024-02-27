/** @odoo-module */

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    //@override
    select_orderline(orderline) {
        super.select_orderline(...arguments);
        if (orderline && orderline.product.id === this.pos.config.down_payment_product_id[0]) {
            this.pos.numpadMode = "price";
        }
    },
    //@override
    _get_ignored_product_ids_total_discount() {
        const productIds = super._get_ignored_product_ids_total_discount(...arguments);
        productIds.push(this.pos.config.down_payment_product_id[0]);
        return productIds;
    },
});

patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        // It is possible that this orderline is initialized using `init_from_JSON`,
        // meaning, it is loaded from localStorage or from export_for_ui. This means
        // that some fields has already been assigned. Therefore, we only set the options
        // when the original value is falsy.
        this.prescription_order_origin_id = this.prescription_order_origin_id || options.prescription_order_origin_id;
        this.prescription_order_line_id = this.prescription_order_line_id || options.prescription_order_line_id;
        this.down_payment_details = this.down_payment_details || options.down_payment_details;
        this.customerNote = this.customerNote || options.customer_note;
        if (this.prescription_order_origin_id && this.prescription_order_origin_id.shipping_date) {
            this.order.setShippingDate(this.prescription_order_origin_id.shipping_date);
        }
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.prescription_order_origin_id = json.prescription_order_origin_id;
        this.prescription_order_line_id = json.prescription_order_line_id;
        this.down_payment_details =
            json.down_payment_details && JSON.parse(json.down_payment_details);
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.prescription_order_origin_id = this.prescription_order_origin_id;
        json.prescription_order_line_id = this.prescription_order_line_id;
        json.down_payment_details =
            this.down_payment_details && JSON.stringify(this.down_payment_details);
        return json;
    },
    get_prescription_order() {
        if (this.prescription_order_origin_id) {
            const value = {
                name: this.prescription_order_origin_id.name,
                details: this.down_payment_details || false,
            };

            return value;
        }
        return false;
    },
    getDisplayData() {
        return {
            ...super.getDisplayData(),
            down_payment_details: this.down_payment_details,
            rx_reference: this.prescription_order_origin_id?.name,
        };
    },
    /**
     * Set quantity based on the give prescription ordder line.
     * @param {'prescription.order.line'} saleOrderLine
     */
    setQuantityFromRXL(saleOrderLine) {
        if (this.product.type === "service") {
            this.set_quantity(saleOrderLine.qty_to_invoice);
        } else {
            this.set_quantity(
                saleOrderLine.product_uom_qty -
                    Math.max(saleOrderLine.qty_delivered, saleOrderLine.qty_invoiced)
            );
        }
    },
});
