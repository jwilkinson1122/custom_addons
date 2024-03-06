/** @odoo-module */

import { usePos } from "@pod_point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@pod_point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";

export class CustomerButton extends Component {
    static template = "pod_point_of_sale.CustomerButton";

    setup() {
        this.pos = usePos();
    }

    get partner() {
        const order = this.pos.get_order();
        return order ? order.get_partner() : null;
    }
}

ProductScreen.addControlButton({
    component: CustomerButton,
    position: ["before", "SetFiscalPositionButton"],
    condition: function () {
        return this.pos.config.module_pos_restaurant;
    },
});
