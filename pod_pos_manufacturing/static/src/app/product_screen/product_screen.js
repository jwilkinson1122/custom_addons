/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

patch(ProductScreen.prototype, {
    releaseSection() {
        const orderOnSection = this.pos.orders.filter(
            (o) => o.sectionId === this.pos.section.id && o.finalized === false
        );
        for (const order of orderOnSection) {
            this.pos.removeOrder(order);
        }
        this.pos.showScreen("FloorScreen");
    },
    showReleaseBtn() {
        return (
            this.pos.config.module_pos_manufacturing &&
            this.pos.section &&
            !this.pos.orders.some(
                (o) =>
                    o.sectionId === this.pos.section.id && o.finalized === false && o.orderlines.length
            )
        );
    },
});
