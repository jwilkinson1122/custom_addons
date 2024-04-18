/** @odoo-module */

import { ProductScreen } from "@point_of_sale/js/Screens/ProductScreen/ProductScreen";
import { usePos } from "@point_of_sale/app/pos_hook";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { SetMeasurmentPopupWidget } from "@wt_abaya/js/Popups/SetMeasurmentPopup";
import { ErrorPopup } from "@point_of_sale/js/Popups/ErrorPopup";
import { PosDB } from "@point_of_sale/js/db";

export class SetMeasurmentButton extends Component {
    static template = "SetMeasurmentButton";

    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
        this.db = new PosDB()
    }
    async click() {
        const order = this.pos.globalState.get_order()
        var partner = order.get_partner();
        var error = "";
        var title = "";
        if(!partner){
            title = "Customer Validation"
            error = "Select Customer first..."
        }else if(!partner.measurment_ids.length){ 
            title = "Measurment Validation"
            error = "This Customer no any measurment!\n\ Add measurment first."
        }else if(!order.get_selected_orderline()){
            title = "Product Validation"
            error = "Set product first."
        }else if(order.get_selected_orderline()){
            if(!order.get_selected_orderline().product.is_tailor_product){
                title = "Non Tailoring"
                error = "Product is not Tailoring product!"
            }
        }
        if(error){
            var body = error
            this.pos.popup.add(ErrorPopup, { title: title, body});
        }else{
            await this.popup.add(SetMeasurmentPopupWidget, {partner:partner});
        }
    }

}

ProductScreen.addControlButton({
    component: SetMeasurmentButton,
    condition: function () {
        return true;
    },
});