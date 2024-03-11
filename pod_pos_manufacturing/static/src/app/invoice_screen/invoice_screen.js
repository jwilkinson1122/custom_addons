/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { registry } from "@web/core/registry";

export class InvoiceScreen extends ReceiptScreen {
    static template = "pod_pos_manufacturing.InvoiceScreen";
    static components = { OrderReceipt };
    confirm() {
        if (!this.env.isMobile) {
            this.props.resolve({ confirmed: true, payload: null });
            this.pos.closeTempScreen();
        }
    }
    /**
     * @override
     */
    async printReceipt() {
        await super.printReceipt();
        this.currentOrder._printed = false;
    }

    get isInvoice() {
        return true;
    }
}

registry.category("pos_screens").add("InvoiceScreen", InvoiceScreen);
