/** @odoo-module **/

import { Component } from "@odoo/owl";

export class ReceiptHeader extends Component {
    static template = "pod_point_of_sale.ReceiptHeader";
    static props = {
        data: {
            type: Object,
            shape: {
                company: Object,
                header: { type: [String, { value: false }], optional: true },
                cashier: { type: String, optional: true },
                "*": true,
            },
        },
    };
}
