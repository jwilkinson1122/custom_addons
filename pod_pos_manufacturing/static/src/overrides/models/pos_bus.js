/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosBus } from "@point_of_sale/app/bus/pos_bus_service";

patch(PosBus.prototype, {
    // Override
    setup() {
        super.setup(...arguments);

        if (this.pos.config.module_pos_manufacturing) {
            this.initSectionOrderCount();
        }
    },

    async initSectionOrderCount() {
        const result = await this.orm.call(
            "pos.config",
            "get_sections_order_count_and_printing_changes",
            [this.pos.config.id]
        );

        this.ws_syncSectionCount(result);
    },

    // Override
    dispatch(message) {
        super.dispatch(...arguments);

        if (message.type === "TABLE_ORDER_COUNT" && this.pos.config.module_pos_manufacturing) {
            this.ws_syncSectionCount(message.payload);
        }
    },

    // Sync the number of orders on each section with other PoS
    // using the same floorplan.
    async ws_syncSectionCount(data) {
        const missingSection = data.find((section) => !(section.id in this.pos.sections_by_id));

        if (missingSection) {
            const result = await this.orm.call("pos.session", "get_pos_ui_manufacturing_floor", [
                [odoo.pos_session_id],
            ]);

            if (this.pos.config.module_pos_manufacturing) {
                this.pos.floors = result;
                this.pos.loadShopFloor();
            }
        }

        for (const floor of this.pos.floors) {
            floor.changes_count = 0;
        }
        for (const section of data) {
            const section_obj = this.pos.sections_by_id[section.id];
            if (section_obj) {
                section_obj.order_count = section.orders;
                section_obj.changes_count = section.changes;
                section_obj.skip_changes = section.skip_changes;
                section_obj.floor.changes_count += section.changes;
            }
        }
    },
});
