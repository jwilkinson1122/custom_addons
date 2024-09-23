/** @odoo-module **/
/*
 * This file is used to register the a new button to see prescription orders data.
 */
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";

class PrescriptionOrdersButton extends Component {
static template = 'pod_prescription_order.PrescriptionOrdersButton';
    setup() {
        this.orm = useService("orm");
        this.pos = usePos();
    }
    async onClick() {
    // fetch all prescription order in draft stage to screen
       var self = this
       await this.orm.call(
            "prescription.order", "all_orders", [], {}
        ).then(function(result) {
            self.pos.showScreen('PrescriptionOrdersScreen', {
                data: result,
                new_order:false
            });
        })
    }
}
ProductScreen.addControlButton({
    component: PrescriptionOrdersButton,
    condition: () => true
})
