/** @odoo-module **/
/*
 * This file is used to add some fields to order class for some reference.
 */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    /**
     * Override the setup method to initialize custom signature properties.
     * @param {Object} options - Options passed to the setup method.
     */
    setup(options) {
        super.setup(...arguments);
         if (options.json) {
        this.prescription_order_id= options.json.prescription_order_id || false;
            this.is_prescription = options.json.is_prescription || false;
            this.prescription_data = options.json.prescription_data || undefined;
     }
    },
    /**
     * Initialize the order object from a JSON representation.
     * @param {Object} json - JSON data representing the order.
     */
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
            // this function is overrided for assigning json value to this
        super.init_from_JSON(...arguments);
        this.prescription_order_id= json.prescription_order_id;
        this.is_prescription = json.is_prescription;
        this.prescription_data = json.prescription_data
    },
    /**
     * Export the order object as a JSON representation.
     * @returns {Object} JSON data representing the order.
     */
    export_as_JSON() {
        //  this function is overrided for assign this to json for new field
        const json = super.export_as_JSON(...arguments);
        json.prescription_order_id=this.prescription_order_id
        json.prescription_data = this.prescription_data;
        json.is_prescription = this.is_prescription;
        return json;
    },
});
