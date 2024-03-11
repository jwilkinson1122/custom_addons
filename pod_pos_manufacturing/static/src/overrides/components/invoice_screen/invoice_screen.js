/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { onWillUnmount } from "@odoo/owl";
import { FloorScreen } from "@pod_pos_manufacturing/app/floor_screen/floor_screen";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        onWillUnmount(() => {
            // When leaving the receipt screen to the floor screen the order is paid and can be removed
            if (this.pos.mainScreen.component === FloorScreen && this.currentOrder.finalized) {
                this.pos.removeOrder(this.currentOrder);
            }
        });
    },
    //@override
    _addNewOrder() {
        if (!this.pos.config.module_pos_manufacturing) {
            super._addNewOrder(...arguments);
        }
    },
    isResumeVisible() {
        if (this.pos.config.module_pos_manufacturing && this.pos.section) {
            return this.pos.getSectionOrders(this.pos.section.id).length > 1;
        }
        return super.isResumeVisible(...arguments);
    },
    //@override
    get nextScreen() {
        if (this.pos.config.module_pos_manufacturing) {
            const section = this.pos.section;
            return { name: "FloorScreen", props: { floor: section ? section.floor : null } };
        } else {
            return super.nextScreen;
        }
    },
});
