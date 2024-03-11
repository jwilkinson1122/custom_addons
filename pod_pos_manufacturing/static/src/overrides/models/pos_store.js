/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { FloorScreen } from "@pod_pos_manufacturing/app/floor_screen/floor_screen";
import { TipScreen } from "@pod_pos_manufacturing/app/tip_screen/tip_screen";
import { ConnectionLostError } from "@web/core/network/rpc_service";

const NON_IDLE_EVENTS = [
    "mousemove",
    "mousedown",
    "touchstart",
    "touchend",
    "touchmove",
    "click",
    "scroll",
    "keypress",
];
let IDLE_TIMER_SETTER;

patch(PosStore.prototype, {
    /**
     * @override
     */
    async setup() {
        this.orderToTransfer = null; // section transfer feature
        this.transferredOrdersSet = new Set(); // used to know which orders has been transferred but not sent to the back end yet
        this.floorPlanStyle = "default";
        this.isEditMode = false;
        await super.setup(...arguments);
        if (this.config.module_pos_manufacturing) {
            this.setActivityListeners();
            this.showScreen("FloorScreen", { floor: this.section?.floor || null });
        }
        this.currentFloor = this.floors?.length > 0 ? this.floors[0] : null;
    },
    setActivityListeners() {
        IDLE_TIMER_SETTER = this.setIdleTimer.bind(this);
        for (const event of NON_IDLE_EVENTS) {
            window.addEventListener(event, IDLE_TIMER_SETTER);
        }
    },
    setIdleTimer() {
        clearTimeout(this.idleTimer);
        if (this.shouldResetIdleTimer()) {
            this.idleTimer = setTimeout(() => this.actionAfterIdle(), 60000);
        }
    },
    async actionAfterIdle() {
        const isPopupClosed = this.popup.closePopupsButError();
        if (isPopupClosed) {
            this.closeTempScreen();
            const section = this.section;
            const order = this.get_order();
            if (order && order.get_screen_data().name === "ReceiptScreen") {
                // When the order is finalized, we can safely remove it from the memory
                // We check that it's in ReceiptScreen because we want to keep the order if it's in a tipping state
                this.removeOrder(order);
            }
            this.showScreen("FloorScreen", { floor: section?.floor });
        }
    },
    getReceiptHeaderData() {
        const json = super.getReceiptHeaderData(...arguments);
        if (this.config.module_pos_manufacturing) {
            if (this.get_order().getSection()) {
                json.section = this.get_order().getSection().name;
            }
            json.customer_count = this.get_order().getCustomerCount();
        }
        return json;
    },
    shouldResetIdleTimer() {
        const stayPaymentScreen =
            this.mainScreen.component === PaymentScreen && this.get_order().paymentlines.length > 0;
        return (
            this.config.module_pos_manufacturing &&
            !stayPaymentScreen &&
            this.mainScreen.component !== FloorScreen
        );
    },
    showScreen(screenName) {
        super.showScreen(...arguments);
        this.setIdleTimer();
    },
    closeScreen() {
        if (this.config.module_pos_manufacturing && !this.get_order()) {
            return this.showScreen("FloorScreen");
        }
        return super.closeScreen(...arguments);
    },
    addOrderIfEmpty() {
        if (!this.config.module_pos_manufacturing) {
            return super.addOrderIfEmpty(...arguments);
        }
    },
    /**
     * @override
     * Before closing pos, we remove the event listeners set on window
     * for detecting activities outside FloorScreen.
     */
    async closePos() {
        if (IDLE_TIMER_SETTER) {
            for (const event of NON_IDLE_EVENTS) {
                window.removeEventListener(event, IDLE_TIMER_SETTER);
            }
        }
        return super.closePos(...arguments);
    },
    showBackButton() {
        return (
            super.showBackButton(...arguments) ||
            this.mainScreen.component === TipScreen ||
            (this.mainScreen.component === ProductScreen && this.config.module_pos_manufacturing)
        );
    },
    //@override
    async _processData(loadedData) {
        await super._processData(...arguments);
        if (this.config.module_pos_manufacturing) {
            this.floors = loadedData["manufacturing.floor"];
            this.loadShopFloor();
        }
    },
    //@override
    async after_load_server_data() {
        var res = await super.after_load_server_data(...arguments);
        if (this.config.module_pos_manufacturing) {
            this.section = null;
        }
        return res;
    },
    //@override
    // if we have sections, we do not load a default order, as the default order will be
    // set when the user selects a section.
    set_start_order() {
        if (!this.config.module_pos_manufacturing) {
            super.set_start_order(...arguments);
        }
    },
    //@override
    add_new_order() {
        const order = super.add_new_order(...arguments);
        this.ordersToUpdateSet.add(order);
        return order;
    },
    async _getSectionOrdersFromServer(sectionIds) {
        this.set_synch("connecting", 1);
        try {
            // FIXME POSREF timeout
            const orders = await this.env.services.orm.silent.call(
                "pos.order",
                "export_for_ui_section_draft",
                [sectionIds]
            );
            this.set_synch("connected");
            return orders;
        } catch (error) {
            this.set_synch("error");
            throw error;
        }
    },
    /**
     * Sync orders that got updated to the back end
     * @param sectionId ID of the section we want to sync
     */
    async _syncSectionOrdersToServer() {
        await this.sendDraftToServer();
        await this._removeOrdersFromServer();
        // This need to be called here otherwise _onReactiveOrderUpdated() will be called after the set is being cleared
        this.ordersToUpdateSet.clear();
        this.transferredOrdersSet.clear();
    },
    /**
     * Replace all the orders of a section by orders fetched from the backend
     * @param sectionId ID of the section
     * @throws error
     */
    async _syncSectionOrdersFromServer(sectionId) {
        await this._removeOrdersFromServer(); // in case we were offline and we deleted orders in the mean time
        const ordersJsons = await this._getSectionOrdersFromServer([sectionId]);
        await this._addPricelists(ordersJsons);
        await this._addFiscalPositions(ordersJsons);
        const sectionOrders = this.getSectionOrders(sectionId);
        this._replaceOrders(sectionOrders, ordersJsons);
    },
    async _getOrdersJson() {
        if (this.config.module_pos_manufacturing) {
            const sectionIds = [].concat(
                ...this.floors.map((floor) => floor.sections.map((section) => section.id))
            );
            await this._syncSectionOrdersToServer(); // to prevent losing the transferred orders
            const ordersJsons = await this._getSectionOrdersFromServer(sectionIds); // get all orders
            await this._loadMissingProducts(ordersJsons);
            return ordersJsons;
        } else {
            return await super._getOrdersJson();
        }
    },
    _shouldRemoveOrder(order) {
        return super._shouldRemoveOrder(...arguments) && !this.transferredOrdersSet.has(order);
    },
    _shouldCreateOrder(json) {
        return (
            (!this._transferredOrder(json) || this._isSameSection(json)) &&
            (!this.selectedOrder || super._shouldCreateOrder(...arguments))
        );
    },
    _shouldRemoveSelectedOrder(removeSelected) {
        return this.selectedOrder && super._shouldRemoveSelectedOrder(...arguments);
    },
    _isSelectedOrder(json) {
        return !this.selectedOrder || super._isSelectedOrder(...arguments);
    },
    _isSameSection(json) {
        const transferredOrder = this._transferredOrder(json);
        return transferredOrder && transferredOrder.sectionId === json.sectionId;
    },
    _transferredOrder(json) {
        return [...this.transferredOrdersSet].find((order) => order.uid === json.uid);
    },
    _createOrder(json) {
        const transferredOrder = this._transferredOrder(json);
        if (this._isSameSection(json)) {
            // this means we transferred back to the original section, we'll prioritize the server state
            this.removeOrder(transferredOrder, false);
        }
        return super._createOrder(...arguments);
    },
    getDefaultSearchDetails() {
        if (this.section && this.section.id) {
            return {
                fieldName: "TABLE",
                searchTerm: this.section.name,
            };
        }
        return super.getDefaultSearchDetails();
    },
    loadShopFloor() {
        // we do this in the front end due to the circular/recursive reference needed
        // Ignore floorplan features if no floor specified.
        this.floors_by_id = {};
        this.sections_by_id = {};
        for (const floor of this.floors) {
            this.floors_by_id[floor.id] = floor;
            for (const section of floor.sections) {
                this.sections_by_id[section.id] = section;
                section.floor = floor;
            }
        }
    },
    async setSection(section, orderUid = null) {
        this.section = section;
        try {
            this.loadingOrderState = true;
            await this._syncSectionOrdersFromServer(section.id);
        } finally {
            this.loadingOrderState = false;
            const currentOrder = this.getSectionOrders(section.id).find((order) =>
                orderUid ? order.uid === orderUid : !order.finalized
            );
            if (currentOrder) {
                this.set_order(currentOrder);
            } else {
                this.add_new_order();
            }
        }
    },
    getSectionOrders(sectionId) {
        return this.get_order_list().filter((order) => order.sectionId === sectionId);
    },
    async unsetSection() {
        try {
            await this._syncSectionOrdersToServer();
        } catch (e) {
            if (!(e instanceof ConnectionLostError)) {
                throw e;
            }
            Promise.reject(e);
        }
        this.section = null;
        this.set_order(null);
    },
    setCurrentOrderToTransfer() {
        this.orderToTransfer = this.selectedOrder;
    },
    async transferSection(section) {
        this.section = section;
        try {
            this.loadingOrderState = true;
            await this._syncSectionOrdersFromServer(section.id);
        } finally {
            this.loadingOrderState = false;
            this.orderToTransfer.sectionId = section.id;
            this.set_order(this.orderToTransfer);
            this.transferredOrdersSet.add(this.orderToTransfer);
            this.orderToTransfer = null;
        }
    },
    getCustomerCount(sectionId) {
        const sectionOrders = this.getSectionOrders(sectionId).filter((order) => !order.finalized);
        return sectionOrders.reduce((count, order) => count + order.getCustomerCount(), 0);
    },
    isOpenOrderShareable() {
        return super.isOpenOrderShareable(...arguments) || this.config.module_pos_manufacturing;
    },
    toggleEditMode() {
        this.isEditMode = !this.isEditMode;
    },
    async updateModelsData(models_data) {
        const floors = models_data["manufacturing.floor"];
        if (floors) {
            this.floors = floors;
            this.loadShopFloor();
            const result = await this.orm.call(
                "pos.config",
                "get_sections_order_count_and_printing_changes",
                [this.config.id]
            );
            for (const section of result) {
                const section_obj = this.sections_by_id[section.id];
                if (section_obj) {
                    section_obj.order_count = section.orders;
                    section_obj.changes_count = section.changes;
                    section_obj.skip_changes = section.skip_changes;
                }
            }
        }
        return super.updateModelsData(models_data);
    },
});
