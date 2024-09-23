/** @odoo-module **/
/*
 * This file is used to register a new screen for Prescription orders.
 */
import { registry } from "@web/core/registry";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

class PrescriptionOrdersScreen extends TicketScreen {
    static template = "pod_prescription_order.PrescriptionOrdersScreen";
    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
    }
    back() {
        this.pos.showScreen('ProductScreen');
    }
    orderDone() {
     // on clicking the back button it will redirected Product screen
    this.pos.add_new_order()
    this.pos.showScreen('ProductScreen');
    }
    async _Confirm(ev) {
    // On clicking confirm button on  each order a order will create with corresponding partner and products,user can do the payment
    var self = this
    var data = ev
    var uid = await  this.orm.call('prescription.order', 'action_confirm',[data.id],{})
    var order = this.pos.orders.find((order) => order.uid == uid);
    var partner_id = data.partner_id
    this.pos.selectedOrder=order
    this.pos.selectedOrder.is_prescription = true
    this.pos.selectedOrder.prescription_data = data
    this.pos.selectedOrder.prescription_order_id = data.id
    this.pos.showScreen('ProductScreen');
}
}
registry.category("pos_screens").add("PrescriptionOrdersScreen", PrescriptionOrdersScreen);
