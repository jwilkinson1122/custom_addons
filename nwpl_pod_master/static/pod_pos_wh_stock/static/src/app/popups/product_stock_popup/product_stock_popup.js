/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";

export class ProductQtyPopup extends AbstractAwaitablePopup {
    static template = "pod_pos_wh_stock.ProductQtyPopup";
    setup() {
        super.setup();
    }
    get getStock() {
        return this.props.product_stock
    }
}
