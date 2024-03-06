/** @odoo-module **/

import { Component } from "@odoo/owl";
import { ReceiptHeader } from "@pod_point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";

export class CashMoveReceipt extends Component {
    static template = "pod_point_of_sale.CashMoveReceipt";
    static components = { ReceiptHeader };
    static props = {
        reason: String,
        translatedType: String,
        formattedAmount: String,
        headerData: Object,
        date: String,
    };
}
