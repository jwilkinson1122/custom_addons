/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        if (this.pos.config.pod_show_qty_location && this.pos.config.pod_display_stock) {
            var order = this.currentOrder;
            var lines = order.get_orderlines()
            var location_id = this.pos.config.pod_pos_location ? this.pos.config.pod_pos_location[0] : false
            if (lines && lines.length) {
                for (let line of lines) {
                    let stock_list = this.pos.db.get_stock_by_product_id(line.get_product().id)
                    if (stock_list){
                        var pod_stock = stock_list.filter((stock) => stock.location_id == location_id)
                        if (pod_stock && pod_stock.length) {
                            pod_stock[0]['quantity'] -= line.quantity
                        }
                    }
                }
            }
        }
        await super.validateOrder(...arguments);
    },
});
