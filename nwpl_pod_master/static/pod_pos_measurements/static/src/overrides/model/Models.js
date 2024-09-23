/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosDB } from "@point_of_sale/app/store/db";
import { Order, Orderline } from "@point_of_sale/app/store/models";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { MeasurementPopup } from "@nwpl_pod_master/static/pod_pos_measurements/app/popups/measurement_popup/MeasurementPopup";
import { SetMeasurementPopup } from "@nwpl_pod_master/static/pod_pos_measurements/app/popups/measurement_popup/MeasurementPopup";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";
import { roundDecimals as round_di, roundPrecision as round_pr } from "@web/core/utils/numbers";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
 
// Patching PosStore
patch(PosStore.prototype, {
    async setup(env, services) {
        await super.setup(env, services);
    },

    async _processData(loadedData) {
        await super._processData(...arguments);
        this._loadMeasurementData(loadedData);
    },

    _loadMeasurementData(loadedData) {
        this.db.measurement_types_by_id = {};
        this.db.measurement_category_by_id = {};
        this.db.measurement_by_id = {};
        this.db.add_measurement_types(loadedData['measurement.type']);
        this.db.add_measurement_categories(loadedData['measurement.measurement.category']);
        this.db.add_measurements(loadedData['measurement.measurement']);
    },

    _loadMeasurementTypes(measurement_type_ids) {
        this.db.measurement_type_by_id = {};
        measurement_type_ids.forEach(element => {
            this.db.measurement_type_by_id[element.id] = element;
        });
    },

    _loadMeasurementCategory(measurement_cat_ids) {
        this.db.measurement_category_by_id = {};
        measurement_cat_ids.forEach(element => {
            this.db.measurement_category_by_id[element.id] = element;
        });
    },

    _loadMeasurements(measurement_ids) {
        this.db.measurement_by_id = {};
        measurement_ids.forEach(element => {
            this.db.measurement_by_id[element.id] = element;
        });
    },
});

// Patching PosDB
patch(PosDB.prototype, {
    async setup() {
        await super.setup(...arguments);
    },

    get_measurement_types_by_id(measurement_type_id) {
        return this._get_by_id(this.measurement_types_by_id, measurement_type_id);
    },

    add_measurement_types(measurement_types) {
        this._add_items_to_dict(this.measurement_types_by_id, measurement_types);
    },

    get_measurement_category_by_id(measurement_cat_ids) {
        return this._get_by_id(this.measurement_category_by_id, measurement_cat_ids);
    },

    add_measurement_categories(measurement_cats) {
        this._add_items_to_dict(this.measurement_category_by_id, measurement_cats);
    },

    get_measurement_by_id(measurement_id) {
        return this._get_by_id(this.measurement_by_id, measurement_id);
    },

    add_measurements(measurements) {
        this._add_items_to_dict(this.measurement_by_id, measurements);
    },

    _get_by_id(dict, ids) {
        if (Array.isArray(ids)) {
            return ids.map(id => dict[id]).filter(Boolean);
        } else {
            return dict[ids];
        }
    },

    _add_items_to_dict(dict, items) {
        items.forEach(item => {
            dict[item.id] = item;
        });
    },
});

// Patching Order

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.measurement_ids = this.measurement_ids || [];
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.measurement_ids = json.measurement_ids || [];
        this.measurement_unit = json.measurement_unit || null;
        this.measurement_date = json.measurement_date || null;
    },

    removeOrderline(line) {
        if (line.Options) {
            line.Options.forEach(option => {
                if (option && option.id) {
                    this.removeOrderline(this.get_orderline(option.id));
                }
            });
        }
        return super.removeOrderline(line);
    },


    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        const orderLines = this.get_orderlines().map(line => {
            const itemJson = line.export_as_JSON();
            if (line.Options) {
                itemJson.Options = line.Options;
            }
            if (line.is_option) {
                itemJson.is_option = line.is_option;
            }
            return [0, 0, itemJson];
        });
        if (orderLines.length > 0) {
            json.lines = orderLines;
        }
        return json;
    },
    
    export_for_printing() {
        const json = super.export_for_printing(...arguments);
        json.measurement_ids = this.measurement_ids;
        json.measurement_unit = this.measurement_unit;
        json.measurement_date = this.measurement_date && formatDate(DateTime.fromJSDate(new Date(this.measurement_date)));
        json.config = this.pos.config;
        return json;
    },

    setMeasurementDate(measurement_date) {
        this.measurement_date = measurement_date;
    },

    getMeasurementDate() {
        return this.measurement_date;
    },

    get_measurement_ids() {
        return this.measurement_ids;
    },

    set_measurement_ids(measurement_ids) {
        console.log("Setting measurement IDs:", measurement_ids);
        this.assert_editable();
        this.measurement_ids = measurement_ids;
    },

    add_product(product, options) {
        const last_orderline = this.get_last_orderline();
        super.add_product(product, options);
        const updated_last_orderline = this.get_last_orderline();
        const popup = this.pos.env.services.popup;

        if (product.measurement_cat_ids && product.measurement_cat_ids.length && !(last_orderline && last_orderline.cid === updated_last_orderline.cid)) {
            const partner = this.get_partner(); // Get the current partner (customer)
            popup.add(SetMeasurementPopup, {
                groups: product.measurement_cat_ids,
                product: product,
                line: updated_last_orderline,
                partner: partner, // Pass the partner object
            });
        }
    }
});

// Patching Orderline
patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.pod_measurement_ids = this.pod_measurement_ids || [];
        this.is_extra_price_set = this.is_extra_price_set || false;
        this.measurement_ids = this.measurement_ids || [];
        this.measurement_unit = null;
        this.extra_price = 0;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        if (json.pod_measurement_ids) {
            this.pod_measurement_ids = json.pod_measurement_ids;
        }
        if (json.is_extra_price_set) {
            this.is_extra_price_set = json.is_extra_price_set;
        }
        if (json.extra_price) {
            this.extra_price = json.extra_price;
        }
        if (json.measurement_ids) {
            this.measurement_ids = json.measurement_ids;
        }
        if (json.measurement_unit) {
            this.measurement_unit = json.measurement_unit;
        }
    },

    export_for_printing() {
        const data = super.export_for_printing();
        data.measurement_data = this.measurement_ids.map(m => {
            return {
                name: m.measurement_type ? m.measurement_type.name : '',
                value: m.measurement
            };
        });
        return data;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.full_product_name = this.get_full_product_name();
        json.pod_measurement_ids = this.pod_measurement_ids;
        json.is_extra_price_set = this.is_extra_price_set;
        json.measurement_ids = this.measurement_ids;
        json.measurement_unit = this.measurement_unit ? this.measurement_unit[0] : null;
        json.extra_price = this.extra_price;
        return json;
    },

    get_orderline_measurements() {
        return this.pod_measurement_ids.map(id => this.pos.db.measurement_by_id[id].name).join('\n');
    },

    set_unit_price(price) {
        if (!this.order) return;  // Check if the order is defined
        this.order.assert_editable();
        let measurement_ids = this.pod_measurement_ids;
        if (measurement_ids && measurement_ids.length && !this.is_extra_price_set) {
            price -= this.extra_price;
            this.extra_price = 0;
            measurement_ids.forEach(element => {
                this.extra_price += this.pos.db.measurement_by_id[element].pos_extra_price;
            });
            this.is_extra_price_set = true;
            price += this.extra_price;
        } else {
            price -= this.extra_price;
            this.extra_price = 0;
        }
        super.set_unit_price(price);
    },

    set_measurement_ids(measurement_ids) {
        console.log("Setting measurement IDs:", measurement_ids);
        if (!this.order) return;  // Check if the order is defined
        this.order.assert_editable();
        this.measurement_ids = measurement_ids;
        this.order.save_to_db();  // Save changes explicitly
    },

    set_measurement_unit(measurement_unit) {
        console.log("Setting measurement units:", measurement_unit);
        if (!this.order) return;  // Check if the order is defined
        this.measurement_unit = measurement_unit;
        this.order.save_to_db();  // Save changes explicitly
    },

    get_orderline_measurements() {
        return this.pod_measurement_ids.map(id => this.pos.db.measurement_by_id[id]?.name || '').join('\n');
    },

    get_measurement_ids() {
        return this.measurement_ids;
    },

    get_measurement_unit() {
        return this.measurement_unit;
    },

    getDisplayData() {
        const data = super.getDisplayData();
        data.measurement_ids = this.measurement_ids;
        data.measurement_unit = this.measurement_unit;
        data.productName = this.get_full_product_name();
        data.is_custom_product = this.get_product().is_custom_product;
        data.product = this.get_product();
        data.full_product_name = this.full_product_name;
        return data;
    }
});

// Patching ProductScreen
patch(ProductScreen.prototype, {
    _setValue(val) {
        const order = this.env.services.pos?.get_order();
        if (order) {
            const order_line = order.get_selected_orderline();
            if (order_line) {
                if (this.env.services.pos.numpadMode === 'price' && val) {
                    order_line.pod_measurement_ids = [];
                }
            }
        }
        super._setValue(val);
    }
});

// Patching ActionpadWidget
patch(ActionpadWidget.prototype, {

    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
    },

    async click() {
        console.log("SetMeasurementButton clicked"); // Debug log
        const order = this.pos.get_order();
        const partner = order.get_partner();
        let error = "";
        let title = "";

        if (!partner) {
            title = "Customer Validation";
            error = "Select Customer first...";
        } else {
            try {
                const partner_measurements = await this.orm.call("res.partner", "get_measurements", [partner.id]);
                this.pos.db.partner_by_id[partner.id].measurement_ids = partner_measurements.map(m => m.id);

                if (!this.pos.db.partner_by_id[partner.id].measurement_ids.length) {
                    const { confirmed } = await this.popup.add(ConfirmPopup, {
                        title: "No Measurements",
                        body: "This customer does not have any measurements. Would you like to add measurements?"
                    });
                    if (confirmed) {
                        console.log("User confirmed to add measurements"); // Debug log

                        await this.popup.add(MeasurementPopup, { partner });
                    }
                    return;
                } else {
                    const orderlines = order.get_orderlines();
                    const allowsMeasurements = orderlines.some(line => line.product.allow_measurements);

                    if (!allowsMeasurements) {
                        title = "No Measurements";
                        error = "No products in the order allow measurements!";
                    }
                }
            } catch (err) {
                console.error("Error loading partner measurements:", err);
                title = "Error";
                error = "There was an error loading the measurements.";
            }
        }

        if (error) {
            console.log("Error encountered:", error); // Debug log
            this.pos.popup.add(ErrorPopup, { title, body: error });
        } else {
            console.log("Opening SetMeasurementPopup"); // Debug log
            await this.popup.add(SetMeasurementPopup, { partner });
        }
    }
});