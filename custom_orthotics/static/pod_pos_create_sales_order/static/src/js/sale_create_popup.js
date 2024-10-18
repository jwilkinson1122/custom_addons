/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";
import { SaleOrderPopup } from "@custom_orthotics/static/pod_pos_create_sales_order/static/src/js/sale_order_popup";
import { Dialog } from "@web/core/dialog/dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";

export class SaleCreatePopup extends Component {
    static template = "pod_pos_create_sales_order.SaleCreatePopup";
    static components = { Dialog }; 

    setup() {
        super.setup();
        this.dialog = useService("dialog");
    }

    static props ={
        pos: { type: Object, required: true },
        getPayload: { type: Function },
        close: { type: Function },
    }
    

    create_order(){
        var self = this;
        var order = self.props.pos.get_order();
        var session_id = self.props.pos.session.id;
        var orderlines = order.lines;
        var cashier_id = self.props.pos.get_cashier().id;
        var partner_id = false;
        var pos_product_list = [];
        var terms = document.getElementById("terms")?.value;
        var ord_state = document.getElementById('ord_state')?.value;

        if (order.get_partner() != null)
            partner_id = order.get_partner().id;

        if (!partner_id) {
            this.props.close();
            return self.env.services.dialog.add(AlertDialog, {
                title: _t("Unknown customer"),
                body: _t( "You cannot Create Sales Order. Select customer first."),
            });
        }

        if (orderlines.length === 0) {
            this.props.close();
            return self.env.services.dialog.add(AlertDialog, {
                title: _t("Empty Order"),
                body: _t( "There must be at least one product in your order."),
            });
        }

        for (var i = 0; i < orderlines.length; i++) {
            var product_items = {
                'id': orderlines[i].product_id.id,
                'quantity': orderlines[i].qty,
                'uom_id': orderlines[i].product_id.uom_id.id,
                'price': orderlines[i].price_unit,
                'discount': orderlines[i].discount,
            };
            pos_product_list.push({'product': product_items });
        }
        self.env.services.orm.call("pod.pos.create.sales.order", "create_sales_order", [
            ,partner_id,pos_product_list, cashier_id, terms, ord_state, session_id]).then(function(output) {
            self.env.services.pos.removeOrder(order);
            self.env.services.pos.add_new_order()
            self.props.close();
            self.env.services.dialog.add(SaleOrderPopup,{'sale_ref': output,})
        });
    }
}
