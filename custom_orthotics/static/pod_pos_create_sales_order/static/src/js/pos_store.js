/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { SaleCreatePopup } from "@custom_orthotics/static/pod_pos_create_sales_order/js/sale_create_popup";
// import { PodSOConfirmPopup } from "@nwpl_pod_master/static/pod_pos_create_so/app/Popups/pod_so_confirm_popup/pod_so_confirm_popup";


patch(PosStore.prototype, {
    async onClick() {
        let pos = this.env.services.pos;
        await makeAwaitable(this.dialog, SaleCreatePopup, {pos: pos});
    }
});
