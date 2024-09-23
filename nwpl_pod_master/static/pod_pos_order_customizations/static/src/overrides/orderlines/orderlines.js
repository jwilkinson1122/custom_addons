/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { PosOrderCustomizationPopup } from "@nwpl_pod_master/static/pod_pos_order_customizations/app/pos_order_customization_popup/PosOrderCustomizationPopup";

patch(Orderline.prototype,{
    setup(){
        super.setup();
    },
    async open_pos_order_customization_popup(){
        var orderline = this.props.line.orderline;
        this.env.services.popup.add(PosOrderCustomizationPopup,{
            groups:orderline.product.customization_group_ids,
            product:orderline.product,
            line:orderline,
        });
    }
})
