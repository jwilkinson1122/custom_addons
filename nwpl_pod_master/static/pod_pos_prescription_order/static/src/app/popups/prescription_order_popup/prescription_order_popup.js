/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


export class PrescriptionOrderPopup extends AbstractAwaitablePopup {
    static template = "pod_prescription_order.PrescriptionOrderPopup";
    static defaultProps = {
        confirmText: _t("Save"),
        cancelText: _t("Discard"),
        clearText: _t("Clear"),
        title: "",
        body: "",
    };
    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
        this.order = this.pos.selectedOrder
        this.order_note= useRef("orderNote")
        this.delivered_date= useRef("deliveryDate")
        this.pickup= useRef("pickup_radio")
        this.delivery= useRef("deliver_radio")
        this.Method_pickup= useRef("Method_pickup")
        this.Method_deliver= useRef("Method_deliver")
    }

    async mounted() {
        this.showHide();
    }

    showHide() {
        if (this.pickup.el && this.Method_pickup.el && this.Method_deliver.el) {
            if (this.pickup.el.checked) {
                this.Method_pickup.el.style.display = 'block';
                this.Method_deliver.el.style.display = 'none';
            }
        }
        if (this.delivery.el && this.Method_pickup.el && this.Method_deliver.el) {
            if (this.delivery.el.checked) {
                this.Method_pickup.el.style.display = 'none';
                this.Method_deliver.el.style.display = 'block';
            }
        }
    }

    async confirm() {
        const order = this.order;
        console.log('Order object:', order);
        console.log('Order properties:', Object.keys(order));
        if (!order.team) {
            // Handle the case where the team is not set, perhaps show an error message
            console.log('Team:', this.order.team);
            console.error("Team is not defined on the order.");
            return;
        }
    
        const team_id = order.team.id;  // This will only run if `order.team` is defined
    
        // Proceed with the rest of the code
        var delivered_date = this.delivered_date.el.value;
        var order_note = this.order_note.el.value;
        var partner = order.partner.id;
        var address = order.partner.address;
        var phone = order.partner.phone;
        var date = order.order_date;
        var line = order.orderlines;
        var pos_order = order.uid;
        var price_list = order.pricelist ? order.pricelist.id : false;
    
        var product = {
            'product_id': [],
            'qty': [],
            'price': []
        };
    
        for (var i = 0; i < line.length; i++) {
            product['product_id'].push(line[i].product.id);
            product['qty'].push(line[i].quantity);
            product['price'].push(line[i].price);
        }
        
        var self = this;
        await this.orm.call(
            "prescription.order", "create_prescription_order", 
            [partner, phone, address, date, price_list, product, order_note, delivered_date, pos_order, team_id], 
            {}
        ).then(function(prescription_order) {
            self.order.prescription_order_id = prescription_order;
        });
    
        await this.orm.call(
            "prescription.order", "all_orders", [], {}
        ).then(function(result) {
            self.pos.showScreen('PrescriptionOrdersScreen', {
                data: result,
                new_order: true
            });
        });
    
        this.cancel();
    }
    

    // async confirm() {
    //     var delivered_date = this.delivered_date.el.value;
    //     var order_note = this.order_note.el.value;
    //     var partner = this.order.partner.id;
    //     var address = this.order.partner.address;
    //     var phone = this.order.partner.phone;
    //     var date = this.order.order_date;
    //     var line = this.order.orderlines;
    //     var pos_order = this.order.uid;
    //     var price_list = this.order.pricelist ? this.order.pricelist.id : false;

    //     var product = {
    //         'product_id': [],
    //         'qty': [],
    //         'price':[]
    //     };

    //     for (var i = 0; i < line.length; i++) {
    //         product['product_id'].push(line[i].product.id)
    //         product['qty'].push(line[i].quantity)
    //         product['price'].push(line[i].price)
    //     }
        
    //     var self = this;
    //     await this.orm.call(
    //         "prescription.order", "create_prescription_order", [partner, phone, address, date, price_list,product, order_note, delivered_date, pos_order], {}
    //     ).then(function(prescription_order) {
    //                 self.order.prescription_order_id=prescription_order
    //     });

    //     await this.orm.call(
    //     "prescription.order", "all_orders", [], {}
    //     ).then(function(result) {
    //         self.pos.showScreen('PrescriptionOrdersScreen', {
    //             data: result,
    //             new_order:true
    //         });
    //     });

    //     this.cancel();
    // }

}
