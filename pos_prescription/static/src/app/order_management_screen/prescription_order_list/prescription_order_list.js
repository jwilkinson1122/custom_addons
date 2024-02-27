/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { PrescriptionOrderRow } from "@pos_prescription/app/order_management_screen/prescription_order_row/prescription_order_row";
import { useService } from "@web/core/utils/hooks";

/**
 * @props {models.Order} [initHighlightedOrder] initially highligted order
 * @props {Array<models.Order>} orders
 */
export class PrescriptionOrderList extends Component {
    static components = { PrescriptionOrderRow };
    static template = "pos_prescription.PrescriptionOrderList";

    setup() {
        this.ui = useState(useService("ui"));
        this.state = useState({ highlightedOrder: this.props.initHighlightedOrder || null });
    }
    get highlightedOrder() {
        return this.state.highlightedOrder;
    }
    _onClickOrder(order) {
        this.state.highlightedOrder = order;
    }
}
