/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";

export class SplitInvoiceButton extends Component {
    static template = "pod_pos_manufacturing.SplitInvoiceButton";

    setup() {
        this.pos = usePos();
    }
    _isDisabled() {
        const order = this.pos.get_order();
        return (
            order
                .get_orderlines()
                .reduce((totalProduct, orderline) => totalProduct + orderline.quantity, 0) < 2
        );
    }
    async click() {
        this.pos.showScreen("SplitInvoiceScreen");
    }
}

ProductScreen.addControlButton({
    component: SplitInvoiceButton,
    condition: function () {
        return this.pos.config.iface_splitinvoice;
    },
});
