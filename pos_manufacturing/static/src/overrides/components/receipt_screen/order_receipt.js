/** @odoo-module */
import { useRef, onMounted, onWillUnmount } from '@odoo/owl';
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { FloorScreen } from "@pos_manufacturing/app/floor_screen/floor_screen";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        // References for A4 Print button and Receipt Container
        this.btnPrintA4 = useRef('btn-print-a4');
        this.posReceiptContainer = useRef('pos-receipt-container');
        
        onMounted(() => this.setA4ButtonVisibility());
        onWillUnmount(() => {
            // When leaving the receipt screen to the floor screen the order is paid and can be removed
            if (this.pos.mainScreen.component === FloorScreen && this.currentOrder.finalized) {
                this.pos.removeOrder(this.currentOrder);
            }
        });
    },

    setA4ButtonVisibility() {
        if (!this.env.pos.config.a4_receipt || this.env.pos.config.a4_receipt_as_default) {
            this.btnPrintA4.el.style.display = 'none';
        }
    },

    async printA4Receipt(ev) {
        const order = this.currentOrder;
        const $currentTarget = $(ev.currentTarget);
        $currentTarget.toggleClass("highlight");
        let mountComponent = $currentTarget.hasClass("highlight") ? 'OrderReceiptA4' : 'OrderReceipt';
        const orderReceipt = new (registry.Component.get(mountComponent))(this, { order });

        let receiptToRemove = this.posReceiptContainer.el ? this.posReceiptContainer.el.querySelectorAll('.pos-receipt') : [];
        receiptToRemove.forEach(el => el.parentNode.removeChild(el));

        await orderReceipt.mount(this.posReceiptContainer.el);
    },

    //@override
    _addNewOrder() {
        if (!this.pos.config.module_pos_manufacturing) {
            super._addNewOrder(...arguments);
        }
    },
    isResumeVisible() {
        if (this.pos.config.module_pos_manufacturing && this.pos.table) {
            return this.pos.getTableOrders(this.pos.table.id).length > 1;
        }
        return super.isResumeVisible(...arguments);
    },
    //@override
    get nextScreen() {
        if (this.pos.config.module_pos_manufacturing) {
            const table = this.pos.table;
            return { name: "FloorScreen", props: { floor: table ? table.floor : null } };
        } else {
            return super.nextScreen;
        }
    },
});
