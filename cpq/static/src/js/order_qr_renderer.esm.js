/** @odoo-module **/

import { Component, onMounted, onWillUpdateProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { generateQrCodeUnified } from "./utils.esm";

class OrderQrRenderer extends Component {
    static template = "cpq.OrderQrRenderer";
    static props = {
        record: Object,
        name: String,  // Standard field props for widgets
    };

    setup() {
        onMounted(() => this._renderQr());
        onWillUpdateProps(() => this._renderQr());
    }

    /**
     * Render QR code when record is available.
     */
    async _renderQr() {
        const orderId = this.props.record?.resId;
        const canvas = this.el.querySelector(".cpq-order-qr-canvas");

        if (!canvas) {
            console.warn("⚠️ No QR canvas element found in template.");
            return;
        }

        if (!orderId) {
            console.warn("⚠️ Order not saved yet — clearing QR code.");
            this._clearCanvas(canvas);
            return;
        }

        const templateId = this.props.record?.data?.product_template_id?.[0] || null;
        const configHash = null;  
        console.log("🟢 Generating QR for Order ID:", orderId);
        generateQrCodeUnified(
            { orderId, templateId, configHash },
            canvas,
            true // Enable debug mode
        );
    }

    /**
     * Clears the QR canvas if the order is not saved.
     */
    _clearCanvas(canvas) {
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    get isUnsaved() {
        return !this.props.record?.resId;
    }
}

export const orderQrField = {
    component: OrderQrRenderer,
    supportedTypes: ["integer"],  // 'id' is an integer field
};

registry.category("fields").add("cpq_order_qr", orderQrField);