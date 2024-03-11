/** @odoo-module **/

import { Component } from "@odoo/owl";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";

export class TipReceipt extends Component {
    static template = "pod_pos_manufacturing.TipReceipt";
    static components = { ReceiptHeader };
    static props = ["headerData", "data", "total"];
}
