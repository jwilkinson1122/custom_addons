/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";

patch(Navbar.prototype, {
    /**
     * If no section is set to pos, which means the current main screen
     * is floor screen, then the order count should be based on all the orders.
     */
    get orderCount() {
        if (this.pos.config.module_pos_shop && this.pos.section) {
            return this.pos.getSectionOrders(this.pos.section.id).length;
        }
        return super.orderCount;
    },
    _shouldLoadOrders() {
        return super._shouldLoadOrders() || this.pos.config.module_pos_shop;
    },
    onSwitchButtonClick() {
        const mode = this.pos.floorPlanStyle == "kanban" ? "default" : "kanban";
        localStorage.setItem("floorPlanStyle", mode);
        this.pos.floorPlanStyle = mode;
    },
    toggleEditMode() {
        this.pos.toggleEditMode();
    },
    showBackButton() {
        return (
            super.showBackButton(...arguments) ||
            (this.pos.showBackButton() && this.pos.config.module_pos_shop)
        );
    },
});
